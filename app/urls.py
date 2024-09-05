from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('sell/<int:product_id>/', views.sell_product, name='sell_product'),
    path('profit-loss/', views.profit_loss_report, name='profit_loss_report'),
    path('analytics/', views.analytics, name='analytics'),
]


