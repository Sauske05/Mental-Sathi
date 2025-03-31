from collections import Counter
from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from django.shortcuts import render
import json
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import httpx
import asyncio
from django.db.models import Q, Avg
# from .models import SentimentModel
import statistics

from reportlab.lib.enums import TA_RIGHT, TA_CENTER

from users.models import User, DashboardRecords
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
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.graphics.shapes import Drawing, String
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
        # today_date = datetime.today().date()
        try:
            if duration == 'weekly':
                sentiment_obj = SentimentDB.objects.filter(
                    Q(user_name=user_obj) & Q(date_time__gte=datetime.today().date() - timedelta(7)))
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


@csrf_exempt
def fetch_bar_sentiment_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        duration = data.get("duration")
        try:
            if duration == 'weekly':
                sentiment_obj = SentimentDB.objects.filter(
                    Q(date_time__gte=datetime.today().date() - timedelta(7)))
            if duration == 'monthly':
                sentiment_obj = SentimentDB.objects.filter(
                    Q(date_time__gte=datetime.today().date() - timedelta(30)))
            if duration == 'all_time':
                sentiment_obj = SentimentDB.objects.all()
            serializer = SentimentSerializer(sentiment_obj, many=True)
            #print(f'This is the serialized data: {JsonResponse(serializer.data, safe=False)}')
            return JsonResponse(serializer.data, safe=False)
        except SentimentDB.DoesNotExist:
            return HttpResponse(status=404)
        except Exception as e:
            return e
    if request.method == "GET":
        try:
            sentiment_obj = SentimentDB.objects.all()
            serializer = SentimentSerializer(sentiment_obj, many=True)
            # print(f'This is the serialized data: {JsonResponse(serializer.data, safe=False)}')
            return JsonResponse(serializer.data, safe=False)
        except SentimentDB.DoesNotExist:
            return HttpResponse(status=404)
        except Exception as e:
            return e


@csrf_exempt
def fetch_admin_table_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            avg_weekly_sentiment = SentimentDB.objects.filter(
                Q(date_time__gte=datetime.today().date() - timedelta(7)) & Q(user_name=user)
            ).aggregate(Avg('sentiment_score'))
            avg_monthly_sentiment = SentimentDB.objects.filter(
                Q(date_time__gte=datetime.today().date() - timedelta(30)) & Q(user_name=user)
            ).aggregate(Avg('sentiment_score'))
            login_streak_data = DashboardRecords.objects.filter(user_name=user).first()
            if login_streak_data:
                login_streak = login_streak_data.login_streak
            else:
                login_streak = None
            weekly_sentiment_score = avg_weekly_sentiment['sentiment_score__avg']
            monthly_sentiment_score = avg_monthly_sentiment['sentiment_score__avg']

            response_dict = {
                'weekly_sentiment_score': weekly_sentiment_score,
                'monthly_sentiment_score': monthly_sentiment_score,
                'login_streak' : login_streak
            }
            print(response_dict)
            return JsonResponse(response_dict, safe=False)
        except Exception as e:
            return e


def sentiment_page(request):
    return render(request, 'sentiment_tracker.html')


async def bert_inference(input_text, bert_model):
    label_dict = {0: 'Anxiety', 1: 'Depression', 2: 'Normal', 3: 'Suicidal', 4: 'Personality disorder'}
    tokenizer_obj = Tokenizer()
    tokenized_input = tokenizer_obj.tokenize([input_text], 100)
    input_ids = tokenized_input['input_ids'].unsqueeze(0)
    print(input_ids.size())
    input_mask_ids = tokenized_input['attention_mask'].unsqueeze(0)
    print(input_mask_ids.size())
    input_mask = input_mask_ids.transpose(-1, -2)
    input_attn_mask = ((input_mask @ input_mask.transpose(-1, -2)).unsqueeze(1))
    bert_model.eval()
    model_pred = bert_model(input_ids, input_attn_mask)
    model_idx = torch.argmax(model_pred[0]).item()  # torch.argmax(model_pred.squeeze())
    if model_idx in label_dict.keys():
        return label_dict[model_idx]


@sync_to_async
def process_initial_data(request, feelings_text, emotion, bert_analysis):
    try:
        score = {
            'Suicidal': -1.0,
            'Depression': -0.9,
            'Anxiety': -0.7,
            'Personality disorder': -0.6,
            'Anxious': -0.4,
            'Sad': -0.5,
            'Angry': -0.4,
            'Calm': -0.0,
            'Normal': 0.3,
            'Excited': 0.7,
            'Happy': 0.9
        }
        try:
            assert emotion in score.keys()
            if bert_analysis:
                average_score = (score[emotion] + score[bert_analysis]) / 2
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
    return report_generator(user_email, False)

def report_generator(user_email, is_task:bool=True):
    user = CustomUser.objects.get(email=user_email)
    print(f'The real user king {user_email}')
    sentiment_data = get_user_sentiment_data_report(user_email)

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Create the PDF object using the buffer as its "file"
    # Using landscape for better visualization of charts
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    # Container for the 'Flowable' objects
    elements = []

    # Enhanced styling
    styles = getSampleStyleSheet()

    # Modern title style
    title_style = ParagraphStyle(
        'ModernTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a73e8'),  # Google blue
        spaceAfter=16,
        fontName='Helvetica-Bold'
    )

    # Modern subtitle style
    subtitle_style = ParagraphStyle(
        'ModernSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#202124'),  # Dark gray
        spaceBefore=12,
        spaceAfter=16,  # Increased space after subtitle
        fontName='Helvetica-Bold',
        borderPadding=10,
        borderWidth=0,
        borderColor=colors.HexColor('#e0e0e0'),
        borderRadius=5
    )

    # Normal text style
    normal_style = ParagraphStyle(
        'ModernNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#5f6368'),  # Medium gray
        fontName='Helvetica'
    )

    # Header style
    header_style = ParagraphStyle(
        'ModernHeader',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9aa0a6'),  # Light gray
        fontName='Helvetica'
    )

    # ===== HEADER SECTION =====
    header_table = Table([['']], colWidths=[doc.width])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f8f9fa')),  # Light gray
        ('BOTTOMPADDING', (0, 0), (0, 0), 0.3 * inch),
        ('TOPPADDING', (0, 0), (0, 0), 0.3 * inch),
    ]))
    elements.append(header_table)

    # ===== TITLE SECTION =====
    current_time = datetime.now().strftime("%B %d, %Y")
    title_data = [
        [Paragraph("<b>SENTIMENT ANALYSIS</b><br/><font size=14 color='#5f6368'>Comprehensive Report</font>",
                   title_style),
         Paragraph(
             f"<font size=9><b>GENERATED</b>: {current_time}</font><br/><font size=8 color='#9aa0a6'>CONFIDENTIAL</font>",
             ParagraphStyle(
                 'DateStyle',
                 parent=normal_style,
                 alignment=TA_RIGHT
             ))]
    ]

    title_table = Table(title_data, colWidths=[4.5 * inch, 4.5 * inch])
    title_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.2 * inch),
    ]))
    elements.append(title_table)

    # Separator line
    elements.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor('#e0e0e0'),
        spaceAfter=0.3 * inch
    ))

    # ===== USER INFORMATION SECTION =====
    elements.append(Paragraph("User Information", subtitle_style))

    # User details in a modern card-like table
    user_data = [
        ["Full Name:", f"{user.first_name} {user.last_name}"],
        ["Email:", user.email],
    ]

    user_table = Table(user_data, colWidths=[1.5 * inch, 7.5 * inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),  # Light gray
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#5f6368')),  # Medium gray
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 0, colors.white),  # No grid lines
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
    ]))

    elements.append(user_table)
    elements.append(Spacer(1, 0.3 * inch))

    # ===== SUMMARY SECTION =====
    elements.append(Paragraph("Sentiment Analysis Summary", subtitle_style))

    # Create a fancy score indicator
    score = sentiment_data['overall_score']
    score_color = colors.HexColor('#34a853') if score >= 7 else colors.HexColor(
        '#fbbc05') if score >= 4 else colors.HexColor('#ea4335')

    summary_data = [
        [
            Paragraph(
                f"<font size=36 color='{score_color.hexval()}'><b>{score:.1f}</b></font><br/><font size=10>OUT OF 10</font>",
                ParagraphStyle('ScoreStyle', alignment=TA_CENTER)),
            Paragraph(f"""
                <b>Analysis Period:</b> {sentiment_data['start_date']} - {sentiment_data['end_date']}<br/>
                <b>Total Items Analyzed:</b> {sentiment_data['total_items']}<br/><br/>
                This report provides an in-depth analysis of sentiment data collected from your 
                account interactions, evaluating the emotional tone across various channels and topics.
            """, normal_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[2 * inch, 7 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),  # Light gray background
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 0, colors.white),  # No grid lines
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 0.4 * inch))

    # ===== SENTIMENT DISTRIBUTION (PIE CHART) =====
    elements.append(Spacer(1, 1 * inch))
    elements.append(Paragraph("Sentiment Distribution", subtitle_style))

    # Create the modern pie chart with INCREASED SIZE
    drawing_pie = Drawing(500, 300)  # Increased from 300x200
    pie = Pie()
    pie.x = 150  # Adjusted x position
    pie.y = 75  # Adjusted y position
    pie.width = 100  # Increased from 100
    pie.height = 100  # Increased from 100
    pie.data = [sentiment_data['positive_percentage'],
                sentiment_data['neutral_percentage'],
                sentiment_data['negative_percentage']]
    pie.labels = None  # No labels on the pie itself

    # Modern color scheme
    pie.slices.strokeWidth = 0
    pie.slices[0].fillColor = colors.HexColor('#34a853')  # Green
    pie.slices[1].fillColor = colors.HexColor('#fbbc05')  # Yellow
    pie.slices[2].fillColor = colors.HexColor('#ea4335')  # Red

    # Add a modern legend
    legend = Legend()
    legend.alignment = 'right'
    legend.x = 310  # Adjusted position
    legend.y = 100  # Adjusted position
    legend.columnMaximum = 1
    legend.fontName = 'Helvetica'
    legend.fontSize = 12  # Increased from 10
    legend.colorNamePairs = [(colors.HexColor('#34a853'), 'Positive'),
                             (colors.HexColor('#fbbc05'), 'Neutral'),
                             (colors.HexColor('#ea4335'), 'Negative')]

    # Add title to the chart
    title = String(150, 260, 'Sentiment Distribution', fontSize=14, fontName='Helvetica-Bold',
                   fillColor=colors.HexColor('#202124'))

    drawing_pie.add(title)
    drawing_pie.add(pie)
    drawing_pie.add(legend)

    elements.append(drawing_pie)
    # elements.append(Spacer(1, 0.2 * inch))

    # ===== SENTIMENT TRENDS (LINE CHART) =====
    elements.append(Paragraph("Sentiment Trends", subtitle_style))

    # Create the modern line chart with INCREASED SIZE
    drawing_line = Drawing(650, 300)  # Increased from 300x200

    lc = HorizontalLineChart()
    lc.x = 50  # Adjusted position
    lc.y = 50  # Adjusted position
    lc.height = 150  # Increased from 110
    lc.width = 550  # Increased from 250
    lc.data = [sentiment_data['trend_data']]
    lc.lines[0].strokeColor = colors.HexColor('#1a73e8')  # Google blue
    lc.lines[0].strokeWidth = 3  # Thicker line

    # Use filled circle markers with larger size
    lc.lines.symbol = makeMarker('FilledCircle')
    # lc.lines.symbol.size = 6  # Larger marker size

    # Configure axes with larger text
    lc.categoryAxis.categoryNames = sentiment_data['trend_dates']
    lc.categoryAxis.labels.boxAnchor = 'ne'
    lc.categoryAxis.labels.angle = 30
    lc.categoryAxis.labels.dy = -10
    lc.categoryAxis.labels.fontName = 'Helvetica'
    lc.categoryAxis.labels.fontSize = 10  # Increased from 8

    lc.valueAxis.valueMin = -1
    lc.valueAxis.valueMax = 1
    lc.valueAxis.valueStep = 0.2
    lc.valueAxis.labels.fontName = 'Helvetica'
    lc.valueAxis.labels.fontSize = 10  # Increased from 8

    # Add better gridlines for readability
    lc.valueAxis.gridStrokeWidth = 0.5
    lc.valueAxis.gridStrokeColor = colors.HexColor('#e0e0e0')

    # Background
    lc.fillColor = colors.HexColor('#f8f9fa')

    # Add title to the chart
    title_line = String(300, 270, 'Sentiment Trends Over Time', fontSize=14, fontName='Helvetica-Bold',
                        fillColor=colors.HexColor('#202124'))

    drawing_line.add(title_line)
    drawing_line.add(lc)

    elements.append(drawing_line)
    # elements.append(Spacer(1, 0.2 * inch))

    # ===== TOPIC ANALYSIS (BAR CHART) =====
    elements.append(Paragraph("Topic Analysis", subtitle_style))

    drawing_bar = Drawing(650, 250)  # Increased from 600x250

    bc = VerticalBarChart()
    bc.x = 50  # Adjusted position
    bc.y = 50  # Adjusted position
    bc.height = 220  # Increased from 150
    bc.width = 550  # Increased from 500
    bc.data = [sentiment_data['topic_scores']]

    # Set fillColor for all bars at once (this fixes the error)
    bc.bars[0].fillColor = colors.HexColor('#1a73e8')  # Google blue

    # Add bar borders
    bc.strokeColor = colors.HexColor('#0d5bba')
    bc.bars.strokeWidth = 1

    # Configure x axis
    bc.categoryAxis.categoryNames = sentiment_data['topics']
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.labels.dy = -10
    bc.categoryAxis.labels.fontName = 'Helvetica'
    bc.categoryAxis.labels.fontSize = 10  # Increased from 8

    # Configure y axis
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 10
    bc.valueAxis.valueStep = 1
    bc.valueAxis.labels.fontName = 'Helvetica'
    bc.valueAxis.labels.fontSize = 10  # Increased from 8

    # Add gridlines for readability
    bc.valueAxis.gridStrokeWidth = 0.5
    bc.valueAxis.gridStrokeColor = colors.HexColor('#e0e0e0')

    # Background
    bc.fillColor = colors.HexColor('#f8f9fa')

    # Add title to the chart
    title_bar = String(300, 310, 'Sentiment by Topic Category', fontSize=14, fontName='Helvetica-Bold',
                       fillColor=colors.HexColor('#202124'))

    drawing_bar.add(title_bar)
    drawing_bar.add(bc)
    elements.append(drawing_bar)
    elements.append(Spacer(1, 0.3 * inch))

    # ===== DETAILED FINDINGS TABLE =====
    elements.append(Paragraph("Detailed Findings", subtitle_style))

    # Create table header with modern styling
    table_header = [["DATE", "SOURCE", "TEXT", "SENTIMENT"]]

    header_table = Table(table_header, colWidths=[1 * inch, 1 * inch, 6 * inch, 1 * inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),  # Google blue
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),  # Increased from 9
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),  # Increased from 8
        ('TOPPADDING', (0, 0), (-1, 0), 10),  # Increased from 8
    ]))

    elements.append(header_table)

    # Add sentiment items with alternating row colors
    for i, item in enumerate(sentiment_data['detailed_items']):
        sentiment_text = item['sentiment']

        # Determine row color
        row_color = colors.HexColor('#f8f9fa') if i % 2 == 0 else colors.white

        # Determine sentiment color badge
        if item['sentiment'] == 'Positive':
            sentiment_color = colors.HexColor('#34a853')  # Green
        elif item['sentiment'] == 'Negative':
            sentiment_color = colors.HexColor('#ea4335')  # Red
        else:
            sentiment_color = colors.HexColor('#fbbc05')  # Yellow

        # Create row data
        row_data = [
            [item['date'],
             item['source'],
             Paragraph(item['text'][:100] + "..." if len(item['text']) > 100 else item['text'], normal_style),
             sentiment_text]
        ]

        row_table = Table(row_data, colWidths=[1 * inch, 1 * inch, 6 * inch, 1 * inch])
        row_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), row_color),
            ('BACKGROUND', (3, 0), (3, 0), sentiment_color),
            ('TEXTCOLOR', (3, 0), (3, 0), colors.white),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (3, 0), (3, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica'),
            ('FONTNAME', (3, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('LEFTPADDING', (0, 0), (-1, 0), 10),
            ('RIGHTPADDING', (0, 0), (-1, 0), 10),
        ]))

        elements.append(row_table)

    # ===== FOOTER SECTION =====
    elements.append(Spacer(1, 0.5 * inch))

    footer_data = [[
        Paragraph(
            "This report is confidential and generated automatically. For questions or support, please contact <font color='#1a73e8'>islingtoncollege.edu.np</font>",
            ParagraphStyle(
                'FooterStyle',
                parent=header_style,
                alignment=TA_RIGHT
            )
        )
    ]]

    footer_table = Table(footer_data, colWidths=[9 * inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    elements.append(footer_table)

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and write response
    pdf = buffer.getvalue()
    buffer.close()
    if is_task is False:
        # Create HTTP response with PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="sentiment_report_{user.username}_{current_time}.pdf"'
        response.write(pdf)

        return response
    else:
        return pdf


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
        return Circle(3, cy=3, r=2, fillColor=colors.blue)


@csrf_exempt
def fetch_sentimentScore(request):
    if request.method == 'POST':
        duration = request.POST.get('duration')
        if request.POST.get('type') == 'all_users':
            data_sentiment_score = None
            match duration:
                case 'weekly':
                    data_sentiment_score = list(SentimentDB.objects.filter(
                        Q(date_time__gte=datetime.today().date() - timedelta(7))).values_list(
                        'sentiment_score', 'date_time'))
                case 'monthly':
                    data_sentiment_score = list(SentimentDB.objects.filter(
                        Q(date_time__gte=datetime.today().date() - timedelta(30))).values_list(
                        'sentiment_score', 'date_time'))
                case 'all_time':
                    data_sentiment_score = list(SentimentDB.objects.all().values_list('sentiment_score', 'date_time'))

            return JsonResponse(data_sentiment_score, safe=False)

        user_email = request.session.get('user_id')
        print(f'User Email test in Django {user_email}')
        user = CustomUser.objects.get(email=user_email)
        print(f'Custom User Object Test in Django {user}')
        # data_sentiment_score = list(SentimentDB.objects.filter(user_name = user).values_list('sentiment_score', 'date_time'))
        data_sentiment_score = list(SentimentDB.objects.filter(
            Q(user_name=user) & Q(date_time__gte=datetime.today().date() - timedelta(7))).values_list('sentiment_score',
                                                                                                      'date_time'))
        return JsonResponse(data_sentiment_score, safe=False)


def fetch_mood_saved_data(request):
    user_email = request.session.get('user_id')
    print('The user email', user_email)
    user = CustomUser.objects.get(email=user_email)
    if request.method == 'GET':
        mood_data = DashboardRecords.objects.filter(user_name=user).values_list('mood_saved_time', 'is_mood_saved')
        mood_data = list(*mood_data)
        print(f'Mood data fetch test : {mood_data}')
        return JsonResponse({
            'mood_saved_time' : mood_data[0],
            'is_mood_saved': mood_data[1]
        }, safe=False)

    if request.method == 'PUT':
        data = json.loads(request.body)
        if data.get('mood_update') is True:
            mood_data_update = DashboardRecords.objects.get(user_name=user)
            mood_data_update.mood_saved_time = datetime.today().date()
            mood_data_update.save()
            return JsonResponse({
                'response' : 'Successfully Update the mood data'
            })
        else:
            return JsonResponse({
                'response' : 'Mood Update Failed'
            })



