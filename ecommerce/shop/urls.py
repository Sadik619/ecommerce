
from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),

    path('product/create/', views.product_create, name='product_create'),

    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    path('product/<int:product_id>/update/', views.product_update, name='product_update'),

    path('product/<int:product_id>/delete/', views.product_delete, name='product_delete'),

    path('cart/', views.view_cart, name='view_cart'),

    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('recently-viewed/', views.recently_viewed_products, name='recently_viewed'),

    path('profile/', views.profile_view, name='profile_view'),

    path('orders/', views.order_list, name='order_list'),
]
