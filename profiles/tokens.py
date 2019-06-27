from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class SignUpTokenGenerator(PasswordResetTokenGenerator):
    """
    Token generation class for email confirmation after signnig up.
    """

    def make_token(self, user, code):
        """"
        Generates token with prepended invitation code and user.id 
        token example: z4ZW0StNfa-4-57j-7f7f647becb1b2973a55
        """
        token = super().make_token(user)
        if '-' in code:
            raise ValueError('No dashes in code allowed')
        return '-'.join([code, str(user.id), token])

    def parse_token(self, token):
        """
        This method returns None if token is invalid or expired.
        Esle - it returns user object with attached invitation code.
        """
        parts = token.split('-', 2)
        if len(parts) != 3:
            return None
        code, user_id, token = parts

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        if user.is_active or user.last_login is not None:
            # already registered
            return None

        if self.check_token(user, token):
            user.invitation_code = code
            return user

    def _make_hash_value(self, user, timestamp):
        """
        this method is overriden because user.last_login is always None
        and use.pk is used explicitly in token
        """
        return user.username + user.password + str(timestamp)


sign_up_token_generator = SignUpTokenGenerator()
