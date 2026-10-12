from django.db import models


class Product(models.Model):
    """Товар маркетплейса. offer_id — артикул продавца в Ozon."""

    offer_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=512)
    category = models.CharField(max_length=255, blank=True, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=16, default="demo")  # demo | ozon
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.offer_id} — {self.name}"


class PriceHistory(models.Model):
    """История изменения цены — основа для графиков и аналитики."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_history")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]
