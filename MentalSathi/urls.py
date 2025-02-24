"""
URL configuration for MentalSathi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
#from users.views import view_login
from users import views as user_views
from .views import index, header
from sentiment_analysis import views as sentiment_views
urlpatterns = [
        path("admin/", admin.site.urls),
        path("", index, name="index"),
        path('signup/', user_views.signup, name='signup'),
        path('header/', header, name = 'header'),
        path('api/', include('api.urls')),
        path('user/', include('users.urls')),
        path('login/', user_views.login_view, name = 'login'),
        path('homepage/', user_views.homepage, name = 'homepage'),

        path('admin_dashboard/', user_views.admin_dashboard, name = 'admin_dashboard'),
        path("chat/", include("chatbot.urls")),
        path('dashboard/', user_views.user_dashboard, name = 'user_dashboard'),
        path('user-charts/', user_views.user_charts, name = 'user_charts'),
        path('user-info/', user_views.user_blank, name = 'user_info' ),
        path('sentiment-tracker/',sentiment_views.sentiment_page, name = 'sentiment'),
]
