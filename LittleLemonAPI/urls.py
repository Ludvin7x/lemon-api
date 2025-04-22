from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuItemViewSet, CategoryDetailView, CategoryListView

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet, basename='menuitem')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]