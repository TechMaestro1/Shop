from django.urls import path

from E_Shop_Frontend.Products import views

urlpatterns = [
    # Error page
    path('404/', views.CancelProduct.as_view(), name='404'),

    # Search View
    path('search/', views.SearchView.as_view(), name='search'),

    # Buy one product
    path('product/<uuid:product_id>/pay/', views.PaymentView.as_view(), name='payment_pro'),



]
