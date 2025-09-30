from django.urls import path
from .views import health
from .views_chat import chat, recommend, upload_report, get_recommendation

urlpatterns = [
    path('health/', health, name='Health'),
    path('chat', chat, name='Chat'),
    path('recommend', recommend, name='Recommend'),
    path('upload_report', upload_report, name='UploadReport'),
    path('get_recommendation', get_recommendation, name='GetRecommendation'),
]
