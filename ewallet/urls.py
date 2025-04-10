from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from wallet.views import AuditLogListView  # Import the missing view

urlpatterns = [
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/auth/', include('wallet.auth_urls')),
    path('api/wallet/', include('wallet.urls')),
    path('api/audit-logs/', AuditLogListView.as_view(), name='audit-logs'),

]
