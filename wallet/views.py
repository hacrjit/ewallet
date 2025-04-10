from rest_framework import status, permissions, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import WalletSerializer, TransactionSerializer, AuditLogSerializer
from decimal import Decimal, InvalidOperation
from .models import Transaction, Wallet, AuditLog
from django.db import transaction

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
