from rest_framework import status, permissions, generics
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import WalletSerializer, TransactionSerializer, AuditLogSerializer, NotificationSerializer, RegisterSerializer, TokenObtainPairSerializer
from decimal import Decimal, InvalidOperation
from .models import Transaction, Wallet, AuditLog, Notification
from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import AllowAny
import logging
from django.contrib.auth import get_user_model
User = get_user_model()


# Registration View
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

wallet_logger = logging.getLogger('wallet')
user_logger = logging.getLogger('user_activity')

# Custom Token Obtain Pair View
class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token_data = response.data

        access_token = token_data.get("access")
        refresh_token = token_data.get("refresh")

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=False,  # True in production
            samesite='Lax',
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,  # True in production
            samesite='Lax',
        )
        return response

# Logout View
class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out"})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response



# Wallet Views
class WalletDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet = request.user.wallet
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

class ActivateWalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=request.user)
            if not wallet.is_active:
                wallet.is_active = True
                wallet.save()
                return Response({'message': 'Wallet activated'}, status=status.HTTP_200_OK)
            return Response({'message': 'Wallet already active'}, status=status.HTTP_200_OK)

class AddMoneyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            amount = Decimal(str(request.data.get('amount')))
            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, InvalidOperation):
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            try:
                wallet = request.user.wallet
                wallet = Wallet.objects.select_for_update().get(pk = wallet.pk)
            except Wallet.DoesNotExist:
                return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)

            if not wallet.is_active:
                return Response({'error': 'Activate wallet first'}, status=status.HTTP_403_FORBIDDEN)

            wallet.balance += amount
            wallet.save()

            Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='credit',status='success')

            return Response({
                'message': f'₹{amount} added to wallet',
                'new_balance': str(wallet.balance)
            }, status=status.HTTP_200_OK)

class WithdrawMoneyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            amount = Decimal(str(request.data.get('amount')))
            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, InvalidOperation):
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            try:
                wallet = request.user.wallet
                wallet = Wallet.objects.select_for_update().get(pk = wallet.pk)
            except Wallet.DoesNotExist:
                return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)

            if not wallet.is_active:
                return Response({'error': 'Activate wallet first'}, status=status.HTTP_403_FORBIDDEN)

            if wallet.balance < amount:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

            wallet.balance -= amount
            wallet.save()


            Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='debit',status='success')

            return Response({
                'message': f'₹{amount} withdrawn from wallet',
                'new_balance': str(wallet.balance)
            }, status=status.HTTP_200_OK)


class WalletTransferView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sender_wallet = request.user.wallet
        recipient_username = request.data.get('recipient')
        amount = request.data.get('amount')

        # Validate amount
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        # Check wallet status
        if not sender_wallet.is_active:
            return Response({'error': 'Sender wallet not active'}, status=status.HTTP_403_FORBIDDEN)

        if sender_wallet.balance < amount:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        # Get recipient
        try:
            recipient = User.objects.get(username=recipient_username)
            if recipient == request.user:
                user_logger.warning(f"Self-transfer attempt by {request.user.username}")
                return Response({'error': 'Cannot transfer to your own wallet'}, status=status.HTTP_400_BAD_REQUEST)
            recipient_wallet = recipient.wallet
        except User.DoesNotExist:
            return Response({'error': 'Recipient user not found'}, status=status.HTTP_404_NOT_FOUND)

        if not recipient_wallet.is_active:
            return Response({'error': 'Recipient wallet not active'}, status=status.HTTP_403_FORBIDDEN)

        # Atomic transaction
        with transaction.atomic():
            # Debit sender
            sender_wallet.balance -= amount
            sender_wallet.save()
            Transaction.objects.create(wallet=sender_wallet, amount=amount, transaction_type='debit', description =f'Transfer to {recipient.username}')

            # Credit recipient
            recipient_wallet.balance += amount
            recipient_wallet.save()
            Transaction.objects.create(wallet=recipient_wallet, amount=amount, transaction_type='credit', description=f'Transfer from {request.user.username}')

        return Response({
            'message': f'₹{amount} transferred to {recipient.username}',
            'sender_balance': str(sender_wallet.balance),
            'recipient_balance': str(recipient_wallet.balance)
        }, status=status.HTTP_200_OK)
    

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['transaction_type', 'status']

    def get_queryset(self):
        return self.request.user.wallet.transactions.order_by('-timestamp')


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]  # or IsAuthenticated if needed

    def get_queryset(self):
        queryset = AuditLog.objects.all().order_by('-timestamp')
        user = self.request.query_params.get('user')
        action = self.request.query_params.get('action')

        if user:
            queryset = queryset.filter(user=user)
        if action:
            queryset = queryset.filter(action=action)
        return queryset


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
            notif.is_read = True
            notif.save()
            return Response({'message': 'Notification marked as read'})
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=404)