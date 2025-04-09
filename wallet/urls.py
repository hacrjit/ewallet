from django.urls import path
from .views import WalletDetailView, ActivateWalletView, AddMoneyView

urlpatterns = [
    path('', WalletDetailView.as_view(), name='wallet_detail'),
    path('activate/', ActivateWalletView.as_view(), name='activate_wallet'),
    path('add/', AddMoneyView.as_view(), name='add_money'),
]
