from django.db import models
from django.conf import settings


class RealEstateObject(models.Model):
    """
    Модель для описания объекта недвижимости.

    Поля:
        - Основная информация (название, описание, цена, статус, доступность).
        - Локация (страна, город, район, адрес, координаты).
        - Характеристики (площадь, количество комнат, состояние и т.д.).
        - Мультимедиа (ссылки на фото и видео).
        - Связь с брокером, управляющим объектом.
    """

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
    complex_name = models.CharField(max_length=255, blank=True, null=True)
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
    features = models.JSONField(
        default=dict, blank=True, help_text="Дополнительные характеристики объекта"
    )

    # Мультимедиа
    photos = models.JSONField(
        default=list, blank=True, help_text="Ссылки на фотографии"
    )
    videos = models.JSONField(default=list, blank=True, help_text="Ссылки на видео")

    # Связь с брокером
    broker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="real_estate_objects",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_objects",
        help_text="Кто назначил брокера на объект",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ListingPrice(models.Model):
    """
    История изменения цен для объектов недвижимости.

    Поля:
        - listing: Объект недвижимости.
        - currency: Валюта.
        - amount: Сумма.
        - effective_date: Дата вступления цены в силу.
    """

    listing = models.ForeignKey(
        RealEstateObject, on_delete=models.CASCADE, related_name="prices"
    )
    currency = models.CharField(max_length=10, default="USD")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateTimeField()

    def __str__(self):
        return f"{self.listing.name} - {self.amount} {self.currency}"


class Developer(models.Model):
    """
    Модель застройщика.

    Поля:
        - name: Название застройщика.
        - country: Страна.
        - city: Город.
        - contact_info: Контактная информация (JSON).
        - rating: Рейтинг застройщика.
    """

    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    contact_info = models.JSONField(default=dict)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.name


class ListingStatusHistory(models.Model):
    """
    История изменения статуса объекта недвижимости.

    Поля:
        - listing: Объект недвижимости.
        - status: Новый статус.
        - changed_at: Дата изменения статуса.
    """

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
    """
    Модель каталога объектов недвижимости.

    Поля:
        - name: Название каталога.
        - description: Описание.
        - is_public: Флаг публичности.
        - broker: Брокер, владелец каталога.
        - tags: Теги для каталога.
        - SEO-поля: Заголовок, описание, ключевые слова.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    broker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="catalogs",
        related_query_name="catalog",
    )
    tags = models.JSONField(default=list, blank=True)
    seo_meta_title = models.CharField(max_length=255, blank=True, null=True)
    seo_meta_description = models.TextField(blank=True, null=True)
    seo_keywords = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CatalogListing(models.Model):
    """
    Связь между каталогом и объектом недвижимости.

    Поля:
        - catalog: Каталог.
        - listing: Объект недвижимости.
        - sort_order: Порядок сортировки в каталоге.
        - notes: Заметки брокера.
    """

    catalog = models.ForeignKey(
        Catalog, on_delete=models.CASCADE, related_name="listings"
    )
    listing = models.ForeignKey(
        RealEstateObject, on_delete=models.CASCADE, related_name="catalogs"
    )
    sort_order = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.catalog.name} - {self.listing.name}"
