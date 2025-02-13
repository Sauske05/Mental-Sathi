# #from .load import load_bert_model
#
# from ai_models.bert_model.tokenizer import Tokenizer
# import torch
#
# from ai_models.bert_model.model import SentimentModel
# from ai_models.bert_model.configure import config
#
# def load_bert_model():
#     model = SentimentModel(config()['h'], config()['d_model'], config()['d_ff'], config()['labels'])
#     model.load_state_dict(torch.load('./bert_model/model_state_dict.pth', weights_only=True))
#     return model
#
#
# bert_model = load_bert_model()
#
# def bert_inference(input_text):
#     label_dict = {0 : 'Anxiety', 1 : 'Depression', 2 : 'Normal', 3 : 'Suicidal', 4 : 'Personality disorder'}
#     tokenizer_obj = Tokenizer()
#     tokenized_input = tokenizer_obj.tokenize([input_text], 100)
#     input_ids = tokenized_input['input_ids'].unsqueeze(0)
#     print(input_ids.size())
#     input_mask_ids = tokenized_input['attention_mask'].unsqueeze(0)
#     print(input_mask_ids.size())
#     input_mask = input_mask_ids.transpose(-1,-2)
#     input_attn_mask = ((input_mask @ input_mask.transpose(-1,-2)).unsqueeze(1))
#     bert_model.eval()
#     model_pred = bert_model(input_ids, input_attn_mask)
#     model_idx = torch.argmax(model_pred[0]).item() #torch.argmax(model_pred.squeeze())
#     if model_idx in label_dict.keys():
#         return  input_text,label_dict[model_idx]
#
#
