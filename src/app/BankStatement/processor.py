import os
from pathlib import Path
import torch
import time
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer

# OCR imports
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

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
        if not pdf_text or not pdf_text.strip():
            raise ValueError("Input text cannot be empty")
            
        start_time = time.time()
        
        prompt = self.prepare_prompt(pdf_text)
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=2048)
        # Move inputs to same device as model
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)
        
        print("Generating output...")
        with torch.inference_mode():
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=2048,
                do_sample=False,
                temperature=0.0,
                top_p=1.0,
                repetition_penalty=1.1,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        # Only decode the new tokens (excluding the input prompt)
        input_length = input_ids.shape[1]
        generated_tokens = outputs[0][input_length:]
        result = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        print(f"Processing completed in {time.time() - start_time:.2f} seconds")

        print("Raw output: ")
        print(result)

        # find json in all the text
        json_start = result.find("{")
        json_end = result.rfind("}") + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("No valid JSON found in the output")

        return result[json_start:json_end]

    def prepare_prompt(self, pdf_text):
        return """
You are an expert ai processor/programmar trained to process raw text extracted from a bank statement PDF to JSON.  Your task is to extract clean, accurate, and consistent structured JSON containing account details and transactions.
Strict rules to follow:
1. JSON structure must follow this format:
{
  "bank_name": "extract bank name",
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
      "closing_balance": number or null,
      "transactions": [
        {
          "date": "YYYY-MM-DD",
          "description": "string",
          "debit": number (if debit) OR
          "credit": number (if credit),
          "balance": number or null,
          "note": "string or null"
        }
      ]
    }
  ]
}
2. Only use one of "debit" or "credit" per transaction. Always use positive numbers.
3. Dates must be formatted as YYYY-MM-DD. If the year is missing, infer from the context of the statement (e.g., January 2024).
4. The "note" field must contain additional reference or invoice info found directly under the transaction line (e.g., masked account numbers, invoice numbers). If none exists, use null.
5. If "balance" is shown in the statement for that transaction, include it. If not, use null.
6. All transactions should belong to the nearest account section above them.
7. Do not include headers, footers, legal disclaimers, or irrelevant text. Focus only on account sections and transaction details.
8. If any required data is missing or unreadable, return null for that field.
9. Do not guess, create, or infer beyond what is in the document. Just extract.
Remember: extract ALL DATA, follow the structure exactly, and never include extra explanation or formatting.
INPUT TEXT:
""" + pdf_text + """
STRICT VALID JSON OUTPUT:
"""

    def extract_pdf_text_ocr(self, pdf_path):
        if not OCR_AVAILABLE:
            raise RuntimeError("OCR libraries not available. Install with: pip install pytesseract pdf2image")
        
        try:
            print(f"Using OCR to extract text from: {pdf_path}")
            
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            text = ""
            for i, image in enumerate(images):
                print(f"Processing page {i+1} with OCR...")
                page_text = pytesseract.image_to_string(image)
                print(f"Page {i+1} extracted {len(page_text)} characters")
                text += page_text + "\n"
            
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to extract text using OCR: {str(e)}")

if __name__ == "__main__":
    processor = BankStatementProcessor()
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(script_dir, "resources", "May_Bank_2024-07.pdf")
        bank_statements_text = processor.extract_pdf_text_ocr(pdf_path)

        result = processor.process(bank_statements_text)
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
