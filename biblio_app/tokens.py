from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            force_bytes(user.pk) + force_bytes(timestamp) + force_bytes(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()
