from django.urls import path
from E_Shop_API.E_Shop_Products import views

urlpatterns = [
    # CRUD permissions Is_admin
    path('create-product/', views.ProductCreateView.as_view(), name='create_product'),
    path('product/<uuid:pk>/', views.ProductView.as_view(), name='product_detail'),

    # Whole Item List
    path('products/', views.ProductListView.as_view(), name='all_product'),
]
