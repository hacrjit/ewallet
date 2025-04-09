from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Wallet
from .serializers import WalletSerializer
from decimal import Decimal, InvalidOperation

class WalletDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet = request.user.wallet
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

class ActivateWalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        wallet = request.user.wallet
        if not wallet.is_active:
            wallet.is_active = True
            wallet.save()
            return Response({'message': 'Wallet activated'}, status=status.HTTP_200_OK)
        return Response({'message': 'Wallet already active'}, status=status.HTTP_200_OK)

class AddMoneyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Get the wallet instance, not the balance
        try:
            wallet = request.user.wallet  # Assuming a OneToOne relation named 'wallet'
        except AttributeError:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)

        if not wallet.is_active:
            return Response({'error': 'Activate wallet first'}, status=status.HTTP_403_FORBIDDEN)

        # Validate and convert amount to Decimal
        amount = request.data.get('amount')
        try:
            # Convert to Decimal directly from string to avoid float precision issues
            amount = Decimal(str(amount))
            if amount <= Decimal('0'):
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, InvalidOperation):
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        # Update balance using Decimal
        wallet.balance += amount
        wallet.save()

        return Response({
            'message': f'₹{amount} added to wallet',
            'new_balance': str(wallet.balance)  # Convert Decimal to string for JSON serialization
        }, status=status.HTTP_200_OK)