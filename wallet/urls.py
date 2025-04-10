from django.urls import path
from .views import WalletDetailView, ActivateWalletView, AddMoneyView, WithdrawMoneyView, TransactionListView, AuditLogListView

urlpatterns = [
    path('', WalletDetailView.as_view(), name='wallet_detail'),
    path('activate/', ActivateWalletView.as_view(), name='activate_wallet'),
    path('add/', AddMoneyView.as_view(), name='add_money'),
    path('withdraw/', WithdrawMoneyView.as_view(), name='withdraw_money'),
    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
]
