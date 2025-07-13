# Load model directly using HF token from .env
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import login

def setup_model():
    load_dotenv()
    
    model = os.getenv("BASE_MODEL")
    hf_token = os.getenv("HF_TOKEN")
    
    if not model:
        raise ValueError("BASE_MODEL environment variable is required")
    
    model_path = Path(__file__).parent / model
    
    # Check if model already exists
    if model_path.exists() and any(model_path.iterdir()):
        print(f"Model already exists at: {model_path}")
        return str(model_path)
    
    # Authenticate with Hugging Face if token is provided
    if hf_token:
        try:
            login(token=hf_token)
            print("Successfully authenticated with Hugging Face")
        except Exception as e:
            print("Continuing without authentication")
    
    try:
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Download tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model, 
            token=hf_token if hf_token else None
        )
        
        # Download model
        model_obj = AutoModelForCausalLM.from_pretrained(
            model, 
            token=hf_token if hf_token else None
        )
        
        # Fix generation config issues before saving
        if hasattr(model_obj, 'generation_config') and model_obj.generation_config is not None:
            gen_config = model_obj.generation_config
            # If do_sample is False, remove temperature to avoid conflicts
            if hasattr(gen_config, 'do_sample') and not gen_config.do_sample:
                if hasattr(gen_config, 'temperature'):
                    gen_config.temperature = None
        
        # Save model and tokenizer
        tokenizer.save_pretrained(model_path)
        model_obj.save_pretrained(model_path)
        
        print(f"Model setup completed successfully at: {model_path}")
        return str(model_path)

    except Exception as e:
        print(f"Error setting up model: {e}")
        raise

if __name__ == "__main__":
    setup_model()