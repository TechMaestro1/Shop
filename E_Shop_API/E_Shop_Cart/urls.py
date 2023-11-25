from django.urls import path
from E_Shop_API.E_Shop_Cart import views

urlpatterns = [
    # CRUD cart  /api/
    path('cart/<uuid:cart_product_id>/', views.CartProductAPIView.as_view(), name='cart_product_api'),

    # Cart list view
    path('cart/', views.CartProductListAPIView.as_view(), name='cart_list_api'),

    # Cart payment processing
    path('payment/', views.PaymentCartAPIView.as_view(), name='payment_api'),
]