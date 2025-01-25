import torch
from transformers import AutoModelForCausalLM, TextStreamer, AutoTokenizer

from ai_models.bert_inference import bert_inference

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_path = './llama_3.2_1B_model'

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map=device)
streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
model.eval()

if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id

input_text, model_pred = bert_inference('''stomach disease anxiety I had spicy chicken three days ago. 
The very next morning tummy ache started.  Also had to go to bathroom for like three times. Took tablets from local pharmacy. 
I felt better by that evening. After two days of this happening, my stomach is stiff, feels like stuffed and looks bigger now. 
Like suddenly it got bigger like I have increased weight!Should I see a  doctor? 
Please help! The anxiety of having some terrible disease is killing me.''')


# prompt = 'Who are you?'
def format_text(user_text, sentiment):
    prompt = f"""
    The user said: "{user_text}"
    The sentiment of the user is: {sentiment}.

    Based on the user's sentiment, generate 3 personalized recommendations to help the user feel better and stay 
    engaged for the day. Focus on activities that are uplifting, calming, or motivating.

    Recommendations:
    """
    return prompt


prompt = format_text(input_text, model_pred)
inputs = tokenizer(prompt, return_tensors='pt').to(device)
attention_mask = inputs["attention_mask"]
with torch.no_grad():
    outputs = model.generate(
        inputs['input_ids'],
        max_length=500,
        no_repeat_ngram_size=1,
        top_k=50,
        temperature=0.7,
        streamer=streamer,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        attention_mask=attention_mask,
        top_p=0.95,
        use_cache=True

    )

generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(generated_text)
