# filters.py

import django_filters
from .models import MenuItem

class MenuItemFilter(django_filters.FilterSet):
    # Filtramos por category__slug usando un filtro de tipo Char
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')

    class Meta:
        model = MenuItem
        fields = ['category']
