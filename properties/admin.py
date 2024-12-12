from django.contrib import admin
from .models import (
    RealEstateObject,
    Catalog,
    CatalogListing,
    Developer,
    ListingPrice,
    ListingStatusHistory,
)


@admin.register(RealEstateObject)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "status", "country", "city", "availability")
    search_fields = ("name", "country", "city", "status")
    list_filter = ("status", "country", "city", "availability")


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ("name", "is_public", "broker")
    search_fields = ("name", "broker__email")
    list_filter = ("is_public",)


@admin.register(CatalogListing)
class CatalogListingAdmin(admin.ModelAdmin):
    list_display = ("catalog", "listing", "sort_order")
    search_fields = ("catalog__name", "listing__name")


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "city", "rating")
    search_fields = ("name", "country", "city")


@admin.register(ListingPrice)
class ListingPriceAdmin(admin.ModelAdmin):
    list_display = ("listing", "currency", "amount", "effective_date")
    search_fields = ("listing__name", "currency")


@admin.register(ListingStatusHistory)
class ListingStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("listing", "status", "changed_at")
    search_fields = ("listing__name", "status")
