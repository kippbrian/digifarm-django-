from django.urls import path
from . import views
from . views import index, ProductHomeView, ProductDetailView, add_to_cart, remove_from_cart, OrderSummaryView, checkoutView, PaymentView, add_coupon, services
app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('product/', ProductHomeView.as_view(), name='product'),
    path('checkout/', checkoutView.as_view(), name='checkout'),
    path('ordersummary/', OrderSummaryView.as_view(), name='ordersummary'),
    path('productdetail/<slug>/', ProductDetailView.as_view(), name='productdetail'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/<code>/', add_coupon, name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('service/', views.services, name='service'),



]
