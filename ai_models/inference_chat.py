# import torch
#
# from transformers import AutoModelForCausalLM, TextStreamer, AutoTokenizer
#
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# device = 'cpu'
# model_path = './llama_3.2_3B_model'
#
# def load_model(model_path_):
#     model = AutoModelForCausalLM.from_pretrained(model_path_, device_map = device)
#     tokenizer = AutoTokenizer.from_pretrained(model_path_)
#     return model, tokenizer
#
def prompt(user_input):
    prompt = f'''
    ###System
    You are a helpful mental health assistant.
    Provide supportive responses to the user.
    ###Input
    {user_input}
    ###Response
    '''
    return prompt

# def inference(model, tokenizer, user_input, streamer, device):
#     prompt_ = prompt(user_input)
#     inputs = tokenizer(prompt_, return_tensors='pt').to(device)
#     attention_mask = inputs["attention_mask"]
#     with torch.no_grad():
#         outputs = model.generate(
#             inputs['input_ids'],
#             max_length=500,
#             no_repeat_ngram_size=1,
#             top_k=5,
#             temperature=0.7,
#             streamer=streamer,
#             eos_token_id=tokenizer.eos_token_id,
#             pad_token_id=tokenizer.pad_token_id,
#             attention_mask=attention_mask,
#             top_p=0.95,
#             use_cache=True,
#         )
#
#     generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     return generated_text
# model, tokenizer = load_model(model_path)
# streamer = TextStreamer(tokenizer, skip_prompt=True,skip_special_tokens=True )
# print(inference(model, tokenizer,'I am sad',streamer,device))