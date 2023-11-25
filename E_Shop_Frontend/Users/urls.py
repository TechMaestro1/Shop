from django.urls import path
from E_Shop_Frontend.Users import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Registration and auto login
    path('registration/', views.RegistrationView.as_view(), name='registration'),

    # Login/Logout
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Forgo/Reset Password and auto login
    path('forgot_password/', views.ForgotPassword.as_view(), name='forgot_password'),
    path('reset_password/', views.PasswordReset.as_view(), name='password_reset'),

    # Send confirmation letter
    path('resend_confirmation/', views.ResendConfirmationView.as_view(), name='resend_confirmation'),
    path('confirm/<str:uid>/<str:token>/', views.ConfirmAccountView.as_view(), name='confirm_account'),

    # Edit User Profile
    path('profile/', views.EditProfileView.as_view(), name='user_profile'),
    path('profile/delete_photo/', views.DeletePhotoView.as_view(), name='delete_photo'),
]
