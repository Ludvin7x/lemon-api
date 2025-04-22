from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MenuItemViewSet,
    CreateOrderView, 
    CategoryDetailView, 
    CategoryListView, 
    OrderViewSet, 
    CartViewSet,
    AssignDeliveryCrewViewSet
)

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet, basename='menuitem')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('order/create/', CreateOrderView.as_view(), name='create-order'),
    path('orders/<int:pk>/assign-delivery-crew/', AssignDeliveryCrewViewSet.as_view({'put': 'assign_delivery_crew'}), name='assign-delivery-crew'),
]