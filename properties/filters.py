import django_filters
from .models import RealEstateObject


class RealEstateObjectFilter(django_filters.FilterSet):
    """
    Фильтры для объектов недвижимости.
    """

    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    country = django_filters.CharFilter(field_name="country", lookup_expr="iexact")
    city = django_filters.CharFilter(field_name="city", lookup_expr="iexact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    ordering = django_filters.OrderingFilter(
        fields=[
            ("price", "price"),
            ("created_at", "created_at"),
        ]
    )

    class Meta:
        model = RealEstateObject
        fields = ["country", "city", "status", "price_min", "price_max"]
