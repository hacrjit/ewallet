from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from wallet.views import AuditLogListView, RegisterView, CookieTokenObtainPairView, LogoutView

urlpatterns = [
    # user registration and authentication
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='token_blacklist'),

    # wallet operations
    path('api/wallet/', include('wallet.urls')),

    # Audit logs
    path('api/audit-logs/', AuditLogListView.as_view(), name='audit-logs'),

]
