from django.urls import path
from E_Shop_API.E_Shop_Users import views

urlpatterns = [
    # CRUD
    path('auth/users/me/', views.MyUserView.as_view(), name='my_user_view'),
    path('auth/users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail_view'),


    # Activate Account
    path('send_activation/', views.SendActivationView.as_view(), name='send_activation'),
    path('activate_user/', views.ActivateUserView.as_view(), name='activate_user'),

    # Forgot password
    path('forgot_password/', views.ForgotPasswordAPI.as_view()),


    # GOOGLE OAUTH PROVIDER
    path('sites/<int:pk>/', views.SiteView.as_view(), name='site_detail'),
    path('provider/<int:pk>/', views.SelectSocialApplicationView.as_view(), name='select_social_application'),
]
