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
                max_new_tokens=1024,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        # Only decode the new tokens (excluding the input prompt)
        input_length = input_ids.shape[1]
        generated_tokens = outputs[0][input_length:]
        result = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        print(f"Processing completed in {time.time() - start_time:.2f} seconds")

        return result

    def prepare_prompt(self, pdf_text):
        return """<|im_start|>user
        SGD Current Account Account Number 04171089735 0pening Balance 24,837.69 01 Jan Payment to IYBB Loan, 11,012.01 13,825.68 *******9715 09 Jan FT vr'a FAST 1 ,050.00 12 .7/5 .68 ClvlA CGl"l AND ANL SECU, *******0103, 0THR- l nvoi ces SGDE02469i , A249?8,0?4980 09 Jan FT vi a FAST Svc Chg 0.50 7? ,715 .18 ClvlA CGMND ANL SECU, *******0103, 0IHR lnvoi ces SGDE024697 , 024928,024980 12 Jan Cheque Deposit SBI 0318033 10,000.00 ?2,775.78 ?2 Jan FT vi a FAST 300.00 2? ,475 .78 Etle rg f-e.en_[ar r n e AS i, t..1111€001- O_Lti R- I NV 24003496 B 1 433603-+6066 ?? Jan FT via FAST Svc Chg - 0.50 22,47 4.68 Evergreen Marine Asi, ********8001, 0THR-lNV 24003496 81143360346066 Total DR/CR Items i0,000.00 12,363.01 USD Current Account Account Number 64770059397 0pen l ng Bal ance 31 Jan Interest Earned 0.30 6 ,904 .7 B 5 ,905 . 0B Total DR/CR I tems '., 0.00 0.30 SGD Term Loan Account Number 44?1007 97 15 01 Jan 01 Jan 31 Jan Bal ance B/F Pni nci pa l Payment lnterest Payment lnterest Billed 10,509.76 You are an expert AI system that extracts structured data from bank statements and outputs ONLY valid JSON. Your task: Extract data from the bank statement text and return ONLY a single, valid JSON object. CRITICAL RULES: 1. Output ONLY valid JSON - no explanations, no comments, no extra text 2. Use proper JSON syntax - double quotes for strings, no trailing commas 3. Use null for missing values, not "null" as a string 4. Numbers must be numeric, not strings 5. Dates must be YYYY-MM-DD format JSON STRUCTURE (follow exactly): { "bank_name": "string", "statement_period": { "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }, "accounts": [ { "account_number": "string", "account_name": "string", "currency": "string", "opening_balance": number, "closing_balance": number, "transactions": [ { "date": "YYYY-MM-DD", "description": "string", "debit": number, "balance": number, "note": "string" } ] } ] } EXTRACTION RULES: - Use either "debit" OR "credit" per transaction, never both - All amounts as positive numbers - Extract account numbers, names, balances exactly as shown - Include ALL transactions found - If data is unclear/missing, use null INPUT TEXT: @m"ybank SGD Current Account Account Number 04171089735 0pening Balance 01 Jan Payment to IYBB Loan, *******9715 09 Jan FT vr'a FAST 1 ,050.00 ClvlA CGl"l AND ANL SECU, *******0103, 0THR- l nvoi ces SGDE02469i 09 Jan FT vi a FAST Svc Chg ClvlA CGMND ANL SECU, *******0103, 12 Jan Cheque Deposit SBI 0318033 ?2 Jan FT vi a FAST 24,837.69 13,825.68 11,012.01 0.50 12 .7/5 .68 , A249?8,0?4980 7? ,715 .18 0IHR lnvoi ces SGDE024697 , 024928,024980 300.00 10,000.00 Etle rg f-e.en_[ar r n e AS i, t..1111€001- O_Lti R- I NV 24003496 B 1 433603-+6066 ?? Jan FT via FAST Svc Chg 0.50 Evergreen Marine Asi, ********8001, 0THR-lNV 24003496 81143360346066 Total DR/CR Items 12,363.01 USD Current Account 6 ,904 .7 B 0.00 5 ,905 . 0B 0.30 Account Number 44?1007 97 15 Bal ance B/F Pni nci pa l Payment lnterest Payment lnterest Billed i0,000.00 0.30 SGD Term Loan 01 Jan 01 Jan 31 Jan 22,47 4.68 Account Number 64770059397 0pen l ng Bal ance 31 Jan Interest Earned Total DR/CR I tems '., ?2,775.78 2? ,475 .78 215,540.0510,509.76 502.25 477 .7A 205 ,030 . 29 244 ,528 .04 245 ,AA5 .7 4 - -.1 All jtems and balances shown above wi l l be consjdened cornect unless Bank js notifjed of any di screpanci es wi thi n 14 days fnom the date of the statement. /l For Investment Accounts: Unit pnice is the bid/NAV price per unit as at the last business day of the calendan month for the respective funds. Nothing in this statement shall be constnued by the unit holden(s) as our investment advice. The information herein is not pnovided as an adviser and we shall not assume any responsibility for the accunacy.and completeness of such infonmation on the perfonmance of any investment made by the unr't holden(s) upon reliance on such information. CSR004P.3101202 4(4085270/04177089735 ) ( S5261 ) ( Pg2l3) (A994) ( N/ L/000000) Maybank Singapore Limited (UEN: 201S04195C) PAGE 2 OF 3 OUTPUT (valid JSON only):
<|im_end|>
<|im_start|>assistant
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
        print('Result: ')
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
