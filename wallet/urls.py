from django.urls import path
from .views import WalletDetailView, ActivateWalletView, AddMoneyView, WithdrawMoneyView, TransactionListView, NotificationListView, MarkNotificationReadView, WalletTransferView

urlpatterns = [
    path('', WalletDetailView.as_view(), name='wallet_detail'),
    path('activate/', ActivateWalletView.as_view(), name='activate_wallet'),
    path('add/', AddMoneyView.as_view(), name='add_money'),
    path('withdraw/', WithdrawMoneyView.as_view(), name='withdraw_money'),
    path('transfer/', WalletTransferView.as_view(), name='wallet_transfer'),
    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
]
