from django.urls import path
from .views import (
    ObjectListCreateView,
    ObjectDetailView,
    CatalogListCreateView,
    CatalogDetailView,
)

urlpatterns = [
    path("objects/", ObjectListCreateView.as_view(), name="object-list"),
    path("objects/<int:pk>/", ObjectDetailView.as_view(), name="object-detail"),
    path("catalogs/", CatalogListCreateView.as_view(), name="catalog-list"),
    path("catalogs/<int:pk>/", CatalogDetailView.as_view(), name="catalog-detail"),
]
