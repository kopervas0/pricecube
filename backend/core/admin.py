from django.contrib import admin

from .models import PriceHistory, Product


class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("offer_id", "name", "category", "price", "stock", "source", "updated_at")
    list_filter = ("category", "source", "is_active")
    search_fields = ("offer_id", "name")
    inlines = [PriceHistoryInline]


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("product", "price", "created_at")
    list_filter = ("created_at",)
