from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

def send_password_reset_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    full_reset_url = request.build_absolute_uri(reset_url)

    message = (
        f"Bonjour {user.username},\n\n"
        "Pour réinitialiser votre mot de passe, cliquez sur le lien ci-dessous :\n"
        f"{full_reset_url}\n\n"
        "Merci d'utiliser notre site !\n"
        f"L'équipe de {request.get_host()}"
    )

    send_mail(
        'Demande de réinitialisation du mot de passe',
        message,
        'from@example.com',  
        [user.email],
        fail_silently=False,
    )
