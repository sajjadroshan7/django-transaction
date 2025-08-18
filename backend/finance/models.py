from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_DOWN

# ===== Supported currencies =====
CURRENCY_CHOICES = [
    ("USD", "US Dollar"),
    ("JPY", "Japanese Yen"),
    ("EUR", "Euro"),
    ("GBP", "British Pound"),
    ("IRR", "Iranian Rial"),
]

# ===== Fake static exchange rates (for demo/testing) =====
FAKE_EXCHANGE_RATES = {
    ("USD", "EUR"): Decimal("0.90"),
    ("EUR", "USD"): Decimal("1.10"),
    ("USD", "JPY"): Decimal("150.00"),
    ("JPY", "USD"): Decimal("0.0067"),
    ("USD", "GBP"): Decimal("0.80"),
    ("GBP", "USD"): Decimal("1.25"),
    ("USD", "IRR"): Decimal("42000.00"),
    ("IRR", "USD"): Decimal("0.000024"),
    ("EUR", "IRR"): Decimal("47000.00"),
    ("IRR", "EUR"): Decimal("0.000021"),
    ("GBP", "IRR"): Decimal("52000.00"),
    ("IRR", "GBP"): Decimal("0.000019"),
    ("JPY", "IRR"): Decimal("300.00"),
    ("IRR", "JPY"): Decimal("0.0033"),
    ("EUR", "GBP"): Decimal("0.88"),  
    ("GBP", "EUR"): Decimal("1.14"),  
}

# ===== Wallet Model =====
class Wallet(models.Model):
    """Represents a user's wallet holding balance in a specific currency."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallets"
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    balance = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    class Meta:
        unique_together = ("user", "currency")

    def __str__(self):
        return f"{self.user.username} - {self.currency} - {self.balance}"

    def clean(self):
        if self.currency not in dict(CURRENCY_CHOICES):
            raise ValidationError(f"Invalid currency: {self.currency}")

    def save(self, *args, **kwargs):
        self.full_clean()
        
        if self.balance is not None:
            self.balance = self.balance.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
        super().save(*args, **kwargs)

# ===== Transaction Model =====
class Transaction(models.Model):
    """Represents a money transfer between two users."""
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_transactions"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_transactions"
    )
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    sender_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    receiver_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def execute_transaction(self, totp_code):
        """Executes the transaction with 2FA, fee, and currency conversion."""

        # ===== Step 1: Verify sender's 2FA token =====
        if not self.sender.verify_token(totp_code):
            raise ValueError("Invalid 2FA code. Transaction denied.")

        # ===== Step 2: Validate currencies =====
        if self.sender_currency not in dict(CURRENCY_CHOICES):
            raise ValueError(f"Invalid sender currency: {self.sender_currency}")
        if self.receiver_currency not in dict(CURRENCY_CHOICES):
            raise ValueError(f"Invalid receiver currency: {self.receiver_currency}")

        # ===== Step 3: Retrieve sender wallet =====
        sender_wallet = Wallet.objects.filter(user=self.sender, currency=self.sender_currency).first()
        if not sender_wallet:
            raise ValueError("Sender does not have a wallet in this currency.")

        # ===== Step 4: Apply transaction fee (5%) =====
        fee = self.amount * Decimal("0.05")
        amount_after_fee = self.amount - fee

        # ===== Step 5: Currency conversion =====
        if self.sender_currency != self.receiver_currency:
            rate = FAKE_EXCHANGE_RATES.get((self.sender_currency, self.receiver_currency), None)
            if rate is None:
                raise ValueError(f"No exchange rate from {self.sender_currency} to {self.receiver_currency}")
            amount_for_receiver = amount_after_fee * rate
        else:
            amount_for_receiver = amount_after_fee

        # ===== Step 6: Ensure sender has enough balance =====
        if sender_wallet.balance < amount_after_fee:
            raise ValueError("Insufficient balance in sender's wallet.")

        # ===== Step 7: Deduct from sender wallet =====
        sender_wallet.balance -= amount_after_fee
        sender_wallet.balance = sender_wallet.balance.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
        sender_wallet.save()

        # ===== Step 8: Add to receiver wallet (or create new) =====
        receiver_wallet, created = Wallet.objects.get_or_create(
            user=self.receiver,
            currency=self.receiver_currency,
            defaults={"balance": amount_for_receiver.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)}
        )
        if not created:
            receiver_wallet.balance += amount_for_receiver
            receiver_wallet.balance = receiver_wallet.balance.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
            receiver_wallet.save()

        # ===== Step 9: Mark transaction as verified =====
        self.verified = True
        self.save()
