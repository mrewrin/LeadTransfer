from django.db import models
from django.conf import settings


class RealEstateObject(models.Model):
    # Основная информация
    name = models.CharField(max_length=255)
    description_ru = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(
        max_length=20,
        choices=[("sale", "Sale"), ("rent", "Rent"), ("sold", "Sold")],
        default="sale",
    )
    availability = models.BooleanField(default=True)

    # Локация
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )

    # Характеристики
    area = models.FloatField(help_text="Общая площадь, кв.м")
    living_area = models.FloatField(
        blank=True, null=True, help_text="Жилая площадь, кв.м"
    )
    land_area = models.FloatField(
        blank=True, null=True, help_text="Площадь участка, кв.м"
    )
    rooms = models.IntegerField()
    bedrooms = models.IntegerField(blank=True, null=True)
    bathrooms = models.IntegerField(blank=True, null=True)
    floors = models.IntegerField(blank=True, null=True)
    total_floors = models.IntegerField(blank=True, null=True)
    year_built = models.IntegerField(blank=True, null=True)
    condition = models.CharField(
        max_length=50,
        choices=[
            ("new", "New"),
            ("renovated", "Renovated"),
            ("needs renovation", "Needs Renovation"),
        ],
        default="new",
    )
    features = models.JSONField(default=dict, blank=True)  # JSON поле для удобств

    # Мультимедиа
    photos = models.JSONField(default=list, blank=True)  # Ссылки на фото
    videos = models.JSONField(default=list, blank=True)  # Ссылки на видео

    # Связь с брокером
    broker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="real_estate_objects",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ListingPrice(models.Model):
    listing = models.ForeignKey(
        RealEstateObject, on_delete=models.CASCADE, related_name="prices"
    )
    currency = models.CharField(max_length=10, default="USD")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateTimeField()

    def __str__(self):
        return f"{self.listing.name} - {self.amount} {self.currency}"


class Developer(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    contact_info = models.JSONField(default=dict)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.name


class ListingStatusHistory(models.Model):
    listing = models.ForeignKey(
        RealEstateObject, on_delete=models.CASCADE, related_name="status_history"
    )
    status = models.CharField(
        max_length=20, choices=[("sale", "Sale"), ("rent", "Rent"), ("sold", "Sold")]
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.listing.name} - {self.status}"


class Catalog(models.Model):
    name = models.CharField(max_length=255)  # Название каталога
    description = models.TextField(blank=True, null=True)  # Описание
    is_public = models.BooleanField(default=False)  # Публичность каталога
    broker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="catalogs",
        related_query_name="catalog",
    )
    tags = models.JSONField(default=list, blank=True)  # Теги для фильтрации
    seo_meta_title = models.CharField(
        max_length=255, blank=True, null=True
    )  # SEO-заголовок
    seo_meta_description = models.TextField(blank=True, null=True)  # SEO-описание
    seo_keywords = models.CharField(
        max_length=255, blank=True, null=True
    )  # SEO-ключевые слова
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CatalogListing(models.Model):
    catalog = models.ForeignKey(
        Catalog, on_delete=models.CASCADE, related_name="listings"
    )  # Каталог
    listing = models.ForeignKey(
        RealEstateObject, on_delete=models.CASCADE, related_name="catalogs"
    )  # Объект недвижимости
    sort_order = models.PositiveIntegerField(default=0)  # Сортировка объекта в каталоге
    notes = models.TextField(
        blank=True, null=True
    )  # Дополнительные заметки брокера для объекта
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.catalog.name} - {self.listing.name}"
