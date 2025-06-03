from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MenuItemViewSet,
    OrderViewSet, 
    CartViewSet,
    ManagerGroupView,
    DeliveryCrewGroupView,
    CreateOrderView,
    AssignDeliveryCrewView,
    OrderDetailView,
    CategoryListView,
    CategoryDetailView,
    RegisterUserView,
)

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet, basename='menuitem')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('orders/create/', CreateOrderView.as_view(), name='create-order'),
    path('orders/<int:pk>/assign-delivery-crew/', AssignDeliveryCrewView.as_view(), name='assign-delivery-crew'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('groups/manager/users/', ManagerGroupView.as_view(), name='manager-group-users'),
    path('groups/manager/users/<int:user_id>/', ManagerGroupView.as_view(), name='manager-group-user-delete'),
    path('groups/delivery-crew/users/', DeliveryCrewGroupView.as_view(), name='delivery-crew-group-users'),
    path('groups/delivery-crew/users/<int:user_id>/', DeliveryCrewGroupView.as_view(), name='delivery-crew-group-user-delete'),
    path('auth/register/', RegisterUserView.as_view(), name='user-register'),
]