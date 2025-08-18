# views.py
from rest_framework import generics, permissions,status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer, UserSerializer

User = get_user_model()


class WalletListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


class TransactionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(sender=self.request.user) | Transaction.objects.filter(receiver=self.request.user)


class TransactionCreateView(generics.CreateAPIView):
    """
    Create a new transaction between users.
    Requires:
        - receiver (user ID)
        - amount
        - sender_currency
        - receiver_currency
        - totp_code
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) 

        sender = request.user
        receiver = serializer.validated_data.get("receiver")
        amount = serializer.validated_data.get("amount")
        sender_currency = serializer.validated_data.get("sender_currency")
        receiver_currency = serializer.validated_data.get("receiver_currency")
        totp_code = serializer.validated_data.get("totp_code")

      
        transaction = Transaction(
            sender=sender,
            receiver=receiver,
            amount=amount,
            sender_currency=sender_currency,
            receiver_currency=receiver_currency
        )
        transaction.execute_transaction(totp_code)

        
        out_serializer = self.get_serializer(transaction)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


class UserListView(generics.ListAPIView):
    """
    Returns all users (id and username).
    Useful for selecting a receiver when creating a transaction.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class CurrencyChoicesView(APIView):
    """
    Since Currency is no longer a model (we are using CHOICES instead),
    this view will return the available currency options.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from .models import CURRENCY_CHOICES
        data = [{"code": code, "name": name} for code, name in CURRENCY_CHOICES]
        return Response(data)


class CreateWalletView(generics.CreateAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WalletsByUserView(generics.ListAPIView):
    """
    Returns wallets for a given user ID.
    GET parameter: ?user_id=<id>
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        if user_id is not None:
            return Wallet.objects.filter(user_id=user_id)
        return Wallet.objects.none()