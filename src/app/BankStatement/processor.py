import os
from pathlib import Path
import torch
import time
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer

class BankStatementProcessor:
    def __init__(self):
        load_dotenv()
        self.device = self.loadBestDevice()
        self.load_model()

    def load_model(self):
        try:
            model_name = os.getenv("BASE_MODEL")
            local_model_path = Path(Path().resolve()) / "src" / "base_model" / model_name
            
            if os.path.exists(local_model_path):
                self.tokenizer = AutoTokenizer.from_pretrained(local_model_path, local_files_only=True)
                self.model = AutoModelForCausalLM.from_pretrained(local_model_path, local_files_only=True)
            else:
                raise RuntimeError(f"Model not found locally. Please download it first using setup_model.py")
            
            # Setup padding token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
            
            self.model.to(self.device)  # Move model to GPU if available
            self.model.config.pad_token_id = self.tokenizer.pad_token_id
            print(f"✅ Model loaded successfully on device: {self.device}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")

    def loadBestDevice(self):
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        return self.device

    def process(self, pdf_text):
        prompt = self.prepare_prompt(pdf_text)
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=8192)
        # Move inputs to same device as model
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)
        
        print("Generating output...")
        with torch.inference_mode():
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=4096,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        # Only decode the new tokens (excluding the input prompt)
        input_length = input_ids.shape[1]
        generated_tokens = outputs[0][input_length:]
        result = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        return result

    def prepare_prompt(self, pdf_text):
        return """<|im_start|>user
Extract complete bank statement data.
Return ONLY valid JSON in the exact structure below. All required fields must be present.

MANDATORY RULES:
  - Each transaction must include:
  - date (in YYYY-MM-DD format)
  - description
  - debit (number if money was withdrawn, null if not)
  - credit (number if money was deposited, null if not)
  - balance (MUST always be present and never null)
  - note (optional, or null)
  - Only one of debit or credit can be non-null.

- Each account must include:
  - account_number
  - account_name
  - currency
  - opening_balance
  - closing_balance
  - list of all associated transactions

- Statement metadata must include:
  - bank_name
  - statement_period with start_date and end_date (format: YYYY-MM-DD)

- Normalize any dates like "01 Jan" to full "YYYY-MM-DD" format using the correct year and month from the document.

JSON OUTPUT STRUCTURE:
{
  "bank_name": "string",
  "statement_period": {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
  },
  "accounts": [
    {
      "account_number": "string",
      "account_name": "string",
      "currency": "string",
      "opening_balance": number,
      "transactions": [
        {
          "date": "YYYY-MM-DD",
          "description": "string",
          "debit": number,
          "credit": number,
          "balance": number,
          "note": "string"
        }
      ]
    }
  ]
}

IMPORTANT: PLEASE MAKE SURE The JSON must be syntactically correct and complete.

Extract from this bank statement:
""" + pdf_text + """
<|im_end|>
<|im_start|>assistant
"""

