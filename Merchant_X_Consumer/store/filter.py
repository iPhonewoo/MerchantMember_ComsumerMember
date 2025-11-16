import django_filters
from store.models import Product, Order
from rest_framework import filters

class InStockFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(stock__gt=0)

class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['iexact', 'icontains'],  # 不區分大小寫的精確匹配和包含匹配
            'price': ['exact', 'lt', 'gt', 'range'],  # 精確匹配、小於、大於和範圍匹配
            'stock': ['exact', 'lt', 'gt', 'range'],  # 精確匹配、小於、大於和範圍匹配
        }

class OrderFilter(django_filters.FilterSet):
    #created_at = django_filters.DateFilter(field_name='created_at__date')
    class Meta:
        model = Order
        fields = {
            'status' : ['exact'],  # 精確匹配
            'created_at' : ['exact', 'lt', 'gt', 'range'],  # 精確匹配、小於、大於和範圍匹配
        }