from django.urls import path
from E_Shop_Frontend.Cart import views

urlpatterns = [
    # CRUD
    path('cart_detail/', views.CartDetailView.as_view(), name='cart_detail'),
    path('add/<uuid:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('update-cart/<uuid:product_id>/', views.UpdateCartView.as_view(), name='update_cart'),
    path('remove/<uuid:product_id>/', views.RemoveCartView.as_view(), name='remove_from_cart'),
    path('empty_cart/', views.EmptyCartView.as_view(), name='empty_cart'),

    # Processing of Payment
    path('cart/payment/', views.PaymentCartView.as_view(), name='payment_cart'),
    path('success_cart/', views.PaymentSuccessView.as_view(), name='payment_success'),
]
