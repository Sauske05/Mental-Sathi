from django.apps import AppConfig
from .bert_model.configure import *
from .bert_model.tokenizer import *
from .bert_model.model import *
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class SentimentAnalysisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sentiment_analysis"
    bert_model = None
    def ready(self):
        model = load_bert()
        model.eval()

        # Store model in class attribute
        SentimentAnalysisConfig.bert_model = model

        print("BERT model loaded at startup!")

def load_bert():
    model = SentimentModel(config()['h'], config()['d_model'], config()['d_ff'], config()['labels'])
    model_path = os.path.join(BASE_DIR, 'sentiment_analysis', 'bert_model', 'model_state_dict.pth')
    model.load_state_dict(torch.load(model_path, weights_only=True, map_location=torch.device('cpu')))
    return model