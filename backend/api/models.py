from django.db import models
from django.contrib.auth.models import AbstractUser
import pyotp
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings

class CustomUser(AbstractUser):
    google_auth_secret = models.CharField(max_length=32, blank=True, null=True)
    google_auth_qr = models.ImageField(upload_to="qrcodes/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.google_auth_secret:
            self.google_auth_secret = pyotp.random_base32()

            
            totp = pyotp.TOTP(self.google_auth_secret)
            uri = totp.provisioning_uri(name=self.username, issuer_name="MyDjangoApp")

            qr = qrcode.make(uri)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            filename = f"{self.username}_qrcode.png"
            self.google_auth_qr.save(filename, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

    def verify_token(self, token):
        totp = pyotp.TOTP(self.google_auth_secret)
        return totp.verify(token)


class Note(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes")

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    image = models.ImageField(upload_to="posts/")
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")

    def __str__(self):
        return self.title
