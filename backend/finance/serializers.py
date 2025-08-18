# serializers.py
from rest_framework import serializers
from .models import Wallet, Transaction
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "currency", "balance"]
        read_only_fields = ["id"]


from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Transaction

User = get_user_model()

class TransactionSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    sender_currency = serializers.ChoiceField(choices=[c[0] for c in Transaction._meta.get_field('sender_currency').choices])
    receiver_currency = serializers.ChoiceField(choices=[c[0] for c in Transaction._meta.get_field('receiver_currency').choices])
    
    totp_code = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "sender",
            "receiver",
            "sender_currency",
            "receiver_currency",
            "amount",
            "timestamp",
            "verified",
            "totp_code",
        ]
        read_only_fields = ["verified", "timestamp", "sender"]

    def create(self, validated_data):
        totp_code = validated_data.pop("totp_code")
        sender = self.context["request"].user
        receiver = validated_data.pop("receiver")
        sender_currency = validated_data.pop("sender_currency")
        receiver_currency = validated_data.pop("receiver_currency")

        transaction = Transaction(
            sender=sender,
            receiver=receiver,
            sender_currency=sender_currency,
            receiver_currency=receiver_currency,
            **validated_data
        )
        transaction.execute_transaction(totp_code)
        return transaction
