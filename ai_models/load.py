from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
from dotenv import load_dotenv
import os
import torch
load_dotenv()
login(os.getenv("HUGGINGFACE_TOKEN"))


def load_llm_model(save_directory, model_name):
    # bnb_config = BitsAndBytesConfig(
    #     load_in_4bit=False,  # Disable 4-bit
    #     load_in_8bit=False,  # Disable 8-bit
    #     quant_method=None  # No quantization method
    # )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, device_map = 'cpu')
    tokenizer.save_pretrained(save_directory)
    model.save_pretrained(save_directory)

    print(f"Model and tokenizer saved to {save_directory}")

#load_model("./llama_3.2_1B_model", "meta-llama/Llama-3.2-1B-Instruct")
#load_model("./llama_3.2_3B_model", "Aspect05/Llama-3.2-3B-Instruct-Mental-Health-FP16")

