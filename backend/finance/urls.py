# urls.py
from django.urls import path
from .views import (
    WalletListView,
    TransactionListView,
    TransactionCreateView,
    CurrencyChoicesView,
    UserListView,
    CreateWalletView,
    WalletsByUserView,
)

urlpatterns = [
    # Wallet endpoints
    path("wallets/", WalletListView.as_view(), name="wallet-list"),
    path("create-wallet/", CreateWalletView.as_view(), name="wallet-create"),

    # Transaction endpoints
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path("transactions/create/", TransactionCreateView.as_view(), name="transaction-create"),

    # Currency endpoints (choices)
    path("currencies/", CurrencyChoicesView.as_view(), name="currency-list"),

    # Users (for selecting receiver)
    path("users/", UserListView.as_view(), name="user-list"),
    path("wallets/by-user/", WalletsByUserView.as_view(), name="wallets-by-user"),
]

