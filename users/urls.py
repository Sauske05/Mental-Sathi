from django.urls import path, include

from .views import *
from django.urls import re_path
from django.views.static import serve
from django.conf import settings

urlpatterns = [

    # path('admin/cards/', card, name='admin_cards'),
    #
    # path('admin/buttons/', buttons, name='admin_buttons'),
    # path('admin/utilities/border/', utilities_border, name='admin_utilities_border'),
    # path('admin/utilities/animation/', utilities_animation, name='admin_utilities_animation'),
    # path('admin/utilities/color/', utilities_color, name='admin_utilities_color'),
    # path('admin/utilities/other/', utilities_other, name='admin_utilities_other'),
    #
    # path('admin/error/', error_page, name='admin_error_page'),
    #
    # path('admin/blank/', blank_page, name='admin_blank_page'),
    # path('admin/charts/', admin_charts, name='admin_charts'),
    path('admin/tables', admin_tables, name='admin_tables'),
    path('user_profile_update/', user_profile_update, name='user_profile_update'),
    path('upload_profile_picture/', upload_profile_picture, name='upload_profile_picture'),
    # re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('request-otp/', request_otp, name='request_otp'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('user_password_update/', user_password_update, name='user_password_update'),
]
