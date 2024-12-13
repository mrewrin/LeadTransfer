from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Настройка для Swagger/Redoc
schema_view = get_schema_view(
    openapi.Info(
        title="LeadTransfer API",
        default_version="v1",
        description="Описание API для LeadTransfer",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="mr.ewrin@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/", include("properties.urls")),
    # Swagger и Redoc
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
