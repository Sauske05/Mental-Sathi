from collections import Counter
from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from django.shortcuts import render
import json
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import httpx
import asyncio
from django.db.models import Q
#from .models import SentimentModel
import statistics
from users.models import User
from .bert_model.configure import *
from .bert_model.tokenizer import *
from .bert_model.model import *
from django.apps import apps
from .models import SentimentModel as SentimentDB
from sentiment_analysis.apps import SentimentAnalysisConfig
from django.db import transaction
from users.models import CustomUser
from .serializers import SentimentSerializer

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import base64
# Create your views here.
@csrf_exempt
def get_user_sentiment_data(request, user_email):
    if request.method == "POST":
        print('Trigger!')
        print(user_email)
        data = json.loads(request.body)
        duration = data.get("duration")
        user_obj = CustomUser.objects.get(email=user_email)
        #today_date = datetime.today().date()
        try:
            if duration == 'weekly':
                sentiment_obj = SentimentDB.objects.filter(Q(user_name=user_obj) & Q(date_time__gte = datetime.today().date() - timedelta(7)))
            if duration == 'monthly':
                sentiment_obj = SentimentDB.objects.filter(
                        Q(user_name=user_obj) & Q(date_time__gte=datetime.today().date() - timedelta(30)))
            if duration == 'all_time':
                sentiment_obj = SentimentDB.objects.filter(user_name=user_obj)
            serializer = SentimentSerializer(sentiment_obj, many=True)
            print(f'This is the serialized data: {JsonResponse(serializer.data, safe=False)}')
            return JsonResponse(serializer.data, safe=False)
        except SentimentDB.DoesNotExist:
            return HttpResponse(status=404)




def sentiment_page(request):
    return render(request, 'sentiment_tracker.html')


async def bert_inference(input_text, bert_model):
    label_dict = {0 : 'Anxiety', 1 : 'Depression', 2 : 'Normal', 3 : 'Suicidal', 4 : 'Personality disorder'}
    tokenizer_obj = Tokenizer()
    tokenized_input = tokenizer_obj.tokenize([input_text], 100)
    input_ids = tokenized_input['input_ids'].unsqueeze(0)
    print(input_ids.size())
    input_mask_ids = tokenized_input['attention_mask'].unsqueeze(0)
    print(input_mask_ids.size())
    input_mask = input_mask_ids.transpose(-1,-2)
    input_attn_mask = ((input_mask @ input_mask.transpose(-1,-2)).unsqueeze(1))
    bert_model.eval()
    model_pred = bert_model(input_ids, input_attn_mask)
    model_idx = torch.argmax(model_pred[0]).item() #torch.argmax(model_pred.squeeze())
    if model_idx in label_dict.keys():
        return  label_dict[model_idx]
@sync_to_async
def process_initial_data(request, feelings_text, emotion, bert_analysis):
    try:
        score = {
            'Suicidal' : -1.0,
            'Depression': -0.9,
            'Anxiety': -0.7,
            'Personality disorder': -0.6,
            'Anxious' : -0.4,
            'Sad': -0.5,
            'Angry' : -0.4,
            'Calm' : -0.0,
            'Normal' : 0.3,
            'Excited' : 0.7,
            'Happy' : 0.9
        }
        try:
            assert emotion in score.keys()
            if bert_analysis:
                average_score = (score[emotion] + score[bert_analysis]) /2
            else:
                average_score = score[emotion]
            with transaction.atomic():
                user_email_session = request.session['user_id']
                print(f'This is the user_name -->>>{user_email_session}')
                user_name = CustomUser.objects.get(email=user_email_session)
                sentiment_obj = SentimentDB(
                    user_name=user_name,
                    sentiment_data=emotion,
                    sentiment_score=average_score,
                    recommendation_text='',  # Will update later
                    user_query=feelings_text,
                    query_sentiment=bert_analysis
                )
                sentiment_obj.save()
                return sentiment_obj.id
        except AssertionError as e:
            print(e)

    except Exception as e:
        print(f"Error saving initial data: {e}")
        return None

@sync_to_async
def update_sentiment_record(sentiment_id, bot_response_):
    if sentiment_id:
        try:
            with transaction.atomic():
                sentiment_obj = SentimentDB.objects.get(id=sentiment_id)
                sentiment_obj.recommendation_text = bot_response_
                sentiment_obj.save()
        except Exception as e:
            print(f"Error updating sentiment record: {e}")
@csrf_exempt
async def sentiment_process(request):
    if request.method == "POST":
            try:
                data = json.loads(request.body)
                feelings_text = data.get("feelingsText")
                emotion = data.get("selectedEmotion")
                bert_model = SentimentAnalysisConfig.bert_model
                bert_analysis = await bert_inference(feelings_text, bert_model)

                sentiment_id = await process_initial_data(request, feelings_text, emotion, bert_analysis)

                prompt_data = {
                    "prompt": f"###System: You are an intelligent and empathetic chatbot capable of providing personalized suggestions to improve the well-being of the user. Your goal is to offer three practical and mood-boosting activities based on the user's current emotional state. Respond with three activities that can help improve someone's mood today. ###User: I'm feeling {emotion} today. {feelings_text} ###Response: ",
                    "max_tokens": 512,
                    "temperature": 0.7
                }

                print(f'Sending data: {json.dumps(prompt_data)}')

                # Create streaming response
                async def stream_llm_response():
                    url = 'http://localhost:2001/recommendation_analysis'
                    timeout = httpx.Timeout(120.0)
                    full_response = ''
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        async with client.stream("POST", url, json=prompt_data) as response:
                            async for chunk in response.aiter_text():
                                # Yield each chunk as it arrives
                                full_response += chunk
                                yield chunk
                    print()
                    await update_sentiment_record(sentiment_id, full_response)
                # Return a streaming response to the frontend
                return StreamingHttpResponse(stream_llm_response(), content_type='text/plain')

            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)


def generate_sentiment_report_pdf(request, user_id):
    user_email = request.session.get('user_id')
    user = CustomUser.objects.get(email=user_email)
    print(f'The real user king {user_email}')
    sentiment_data = get_user_sentiment_data_report(user_email)

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Create the PDF object using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Container for the 'Flowable' objects
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']

    # Custom styles
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray
    )

    # Add company logo/header
    # elements.append(Image('path/to/logo.png', width=2*inch, height=0.5*inch))

    # Add report title
    elements.append(Paragraph("Sentiment Analysis Report", title_style))

    # Add timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Generated on: {current_time}", header_style))
    elements.append(Spacer(1, 0.2 * inch))

    # User Information Section
    elements.append(Paragraph("User Information", subtitle_style))

    # User details table
    user_data = [
        ["Full Name:", f"{user.first_name} {user.last_name}"],
        ["Email:", user.email],
        #["Last Login:", user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else "Never"],
        #["Account Created:", user.date_joined.strftime("%Y-%m-%d %H:%M:%S")]
    ]

    user_table = Table(user_data, colWidths=[1.5 * inch, 4 * inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ]))

    elements.append(user_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Summary Section
    elements.append(Paragraph("Sentiment Analysis Summary", subtitle_style))

    # Example sentiment summary
    sentiment_summary = f"""
    This report provides an analysis of sentiment data collected from your account interactions.
    Overall Sentiment Score: {sentiment_data['overall_score']:.2f}/10
    Total Items Analyzed: {sentiment_data['total_items']}
    Period: {sentiment_data['start_date']} to {sentiment_data['end_date']}
    """
    elements.append(Paragraph(sentiment_summary, normal_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Add pie chart for sentiment distribution
    elements.append(Paragraph("Sentiment Distribution", subtitle_style))

    # Create the pie chart
    drawing = Drawing(400, 200)
    pie = Pie()
    pie.x = 150
    pie.y = 50
    pie.width = 100
    pie.height = 100
    pie.data = [sentiment_data['positive_percentage'],
                sentiment_data['neutral_percentage'],
                sentiment_data['negative_percentage']]
    pie.labels = ['Positive', 'Neutral', 'Negative']
    pie.slices.strokeWidth = 0.5
    pie.slices[0].fillColor = colors.green
    pie.slices[1].fillColor = colors.yellow
    pie.slices[2].fillColor = colors.red

    # Add a legend
    legend = Legend()
    legend.alignment = 'right'
    legend.x = 280
    legend.y = 90
    legend.colorNamePairs = [(colors.green, 'Positive'),
                             (colors.yellow, 'Neutral'),
                             (colors.red, 'Negative')]

    drawing.add(pie)
    drawing.add(legend)
    elements.append(drawing)
    elements.append(Spacer(1, 0.2 * inch))

    # Add time series chart for sentiment trends
    elements.append(Paragraph("Sentiment Trends Over Time", subtitle_style))

    # Create the line chart
    drawing = Drawing(400, 200)

    lc = HorizontalLineChart()
    lc.x = 50
    lc.y = 50
    lc.height = 125
    lc.width = 300
    lc.data = [sentiment_data['trend_data']]
    lc.lines[0].strokeColor = colors.blue
    #lc.lines[0].symbol = makeMarker('Circle')

    # Configure x axis
    lc.categoryAxis.categoryNames = sentiment_data['trend_dates']
    lc.categoryAxis.labels.boxAnchor = 'ne'
    lc.categoryAxis.labels.angle = 30
    lc.categoryAxis.labels.dy = -10

    # Configure y axis
    lc.valueAxis.valueMin = -1
    lc.valueAxis.valueMax = 1
    lc.valueAxis.valueStep = 0.2

    drawing.add(lc)
    elements.append(drawing)
    elements.append(Spacer(1, 0.2 * inch))

    # Add topic sentiment breakdown
    elements.append(Paragraph("Sentiment by Topic", subtitle_style))

    # Create the bar chart
    drawing = Drawing(400, 200)

    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = [sentiment_data['topic_scores']]
    bc.bars[0].fillColor = colors.steelblue

    # Configure x axis
    bc.categoryAxis.categoryNames = sentiment_data['topics']
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.labels.dy = -10

    # Configure y axis
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 10
    bc.valueAxis.valueStep = 1

    drawing.add(bc)
    elements.append(drawing)
    elements.append(Spacer(1, 0.3 * inch))

    # Detailed findings section
    elements.append(Paragraph("Detailed Findings", subtitle_style))

    # Create table for detailed sentiment items
    detailed_data = [["Date", "Source", "Text", "Sentiment"]]

    # Add sample sentiment items
    for item in sentiment_data['detailed_items']:
        sentiment_text = item['sentiment']
        color = colors.green if item['sentiment'] == 'Positive' else colors.red if item[
                                                                                       'sentiment'] == 'Negative' else colors.orange
        detailed_data.append([
            item['date'],
            item['source'],
            Paragraph(item['text'][:100] + "..." if len(item['text']) > 100 else item['text'], normal_style),
            sentiment_text
        ])

    detailed_table = Table(detailed_data, colWidths=[1 * inch, 1 * inch, 3.5 * inch, 1 * inch])
    detailed_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(detailed_table)

    # Add footer
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(
        "This report is confidential and generated automatically. For questions or support, please contact islingtoncollege.edu.np",
        header_style))

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and write response
    pdf = buffer.getvalue()
    buffer.close()

    # Create HTTP response with PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sentiment_report_{user.username}_{current_time}.pdf"'
    response.write(pdf)

    return response



def get_user_sentiment_data_report(user_email):
    print('User Id to be debugged:', user_email)
    user = CustomUser.objects.get(email=user_email)
    sentiment_obj = SentimentDB.objects.filter(user_name=user)
    sentiment_scores = list(sentiment_obj.values_list('sentiment_score', flat=True))
    sentiment_scores = [score for score in sentiment_scores if isinstance(score, float)]
    overall_score = statistics.mean(sentiment_scores) if sentiment_scores else 0
    sentiment_labels = list(sentiment_obj.values_list('sentiment_data', flat=True))
    sentiment_dict = dict(Counter(sentiment_labels))
    date_objects = list(sentiment_obj.values_list('date_time', flat=True))
    date_objects.sort()
    trend_dates = []
    for date in date_objects:
        if isinstance(date, datetime):
            formatted_date = date.strftime('%b %d')
            trend_dates.append(formatted_date)

    total_items = sentiment_obj.count()
    start_date = min(date_objects) if date_objects else None
    end_date = max(date_objects) if date_objects else None

    if sentiment_scores:
        positive_scores = sum(1 for score in sentiment_scores if score > 0.0)
        neutral_scores = sum(1 for score in sentiment_scores if score == 0.0)
        negative_scores = sum(1 for score in sentiment_scores if score < 0.0)

        total_count = len(sentiment_scores)
        positive_percentage = round((positive_scores / total_count) * 100)
        neutral_percentage = round((neutral_scores / total_count) * 100)
        negative_percentage = round((negative_scores / total_count) * 100)
    else:
        positive_percentage = 0
        neutral_percentage = 0
        negative_percentage = 0

    return {
        'overall_score': overall_score,
        'total_items': total_items,
        'start_date': start_date,
        'end_date': end_date,
        'positive_percentage': positive_percentage,
        'neutral_percentage': neutral_percentage,
        'negative_percentage': negative_percentage,
        'trend_data': sentiment_scores,
        'trend_dates': trend_dates,
        'topics': list(sentiment_dict.keys()),
        'topic_scores': list(sentiment_dict.values()),
        'detailed_items': [
            {
                'date': '2025-02-28',
                'source': 'Email',
                'text': 'I really appreciate the quick response from your team. The product works perfectly now!',
                'sentiment': 'Positive'
            },
            {
                'date': '2025-02-25',
                'source': 'Chat',
                'text': 'The interface is confusing and I had trouble finding the settings section.',
                'sentiment': 'Negative'
            },
            {
                'date': '2025-02-20',
                'source': 'Survey',
                'text': 'Overall satisfied with the service but would like to see more features added in the future.',
                'sentiment': 'Neutral'
            },
            {
                'date': '2025-02-15',
                'source': 'Review',
                'text': 'Excellent product, has saved me hours of work every week!',
                'sentiment': 'Positive'
            },
            {
                'date': '2025-02-10',
                'source': 'Support',
                'text': 'The new update resolved all previous issues I was experiencing. Very happy with the improvements.',
                'sentiment': 'Positive'
            }
        ]
    }


# Helper function to create markers for line charts
def makeMarker(name):
    from reportlab.graphics.shapes import Circle
    if name == 'Circle':
        return Circle(3, cy=3, r = 2, fillColor=colors.blue)