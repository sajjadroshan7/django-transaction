from django.contrib.auth.models import User
from .models import CustomUser
from rest_framework import serializers
from .models import Note,Post


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "password", "google_auth_qr"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

class UserProfileSerializer(serializers.ModelSerializer):
    google_auth_qr = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "google_auth_qr","google_auth_secret"]

    def get_google_auth_qr(self, obj):
        request = self.context.get("request")
        if obj.google_auth_qr and request:
            return request.build_absolute_uri(obj.google_auth_qr.url)
        elif obj.google_auth_qr:
            return obj.google_auth_qr.url
        return None


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content", "created_at", "author"]
        extra_kwargs = {"author": {"read_only": True}}


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "image", "content", "created_at", "author"]