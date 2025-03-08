from django.db import transaction
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added, pre_social_login

from users.models import DashboardRecords

@receiver(user_signed_up)
def create_user_profile(request, user, **kwargs):
    """
    Signal handler to create a user profile when a new user signs up with Google.
    This is triggered when a completely new user is created.
    """
    # Get the social account instance
    sociallogin = kwargs.get('sociallogin', None)
    if sociallogin and sociallogin.account.provider == 'google':
        extra_data = sociallogin.account.extra_data

        with transaction.atomic():
            dashboard_init = DashboardRecords(user_name=user, login_streak=1, number_of_login_days=1,
                                              positive_streak=0)
            dashboard_init.save()
            request.session['user_id'] = user.email
