from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from users.models import User


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Called when a new user logs in via Google.
        Extract Google data and save it to the User model.
        """
        user = sociallogin.user
        user.user_name = data.get("name", "")  # Use Google Name as Username
        user.email = data.get("email", "")
        user.profile_picture = data.get("picture", "")  # Google Profile Picture
        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Called when saving a new user.
        """
        user = super().save_user(request, sociallogin, form)
        extra_data = sociallogin.account.extra_data
        user.user_name = extra_data.get("name", "")
        user.email = extra_data.get("email", "")
        user.profile_picture = extra_data.get("picture", "")
        user_obj = User(user_name=user.user_name, email=user.email, profile_picture=user.profile_picture)
        user_obj.save()
        user.save()

        return user
