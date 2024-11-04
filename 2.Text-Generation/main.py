import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    GenerationConfig,
    pipeline,
)

# Device Availability
device = torch.device("xpu" if torch.xpu.is_available() else "cpu")
if device.type == "xpu":
    torch.xpu.empty_cache()
    print(f"Using device: {torch.xpu.get_device_name()}")
else:
    print("Using CPU")

# Model Initialization
model_name = "NousResearch/Hermes-2-Pro-Mistral-7B"
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name)
# Configuration for Generation
generation_config = GenerationConfig.from_pretrained(model_name)
generation_config.max_new_tokens = 512  
generation_config.temperature = 0.1      
generation_config.top_p = 0.85            
generation_config.do_sample = True

# Create a pipeline for text generation
llm = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=device,
    generation_config=generation_config,
    repetition_penalty=1.15,
    return_full_text=False,
    num_return_sequences=1,
    eos_token_id=tokenizer.eos_token_id,
    pad_token_id=tokenizer.eos_token_id,
)

# Taking input from the user
input_text = input("Enter the topic you want to know: ")

# Prompt for the model
prompt = (
    f"You are an expert assistant. Please provide accurate and focused information only about the following topic. "
    f"Do not include any unrelated information or examples.\n"
    f"If you don't know the answer, simply state clearly that you do not know the answer. Do not attempt to generate answers beyond the context. "
    f"Topic: {input_text}\n"
    f"Response:"
)

print("-----Generating the text-----")
# Generate the result
result = llm(prompt)

# Output the result
if result and isinstance(result, list) and len(result) > 0:
    print("Generated Output:")
    print(result[0]['generated_text'])  
else:
    print("No result generated.")
