from rest_framework import serializers

from .models import PriceHistory, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "offer_id",
            "name",
            "category",
            "price",
            "old_price",
            "stock",
            "is_active",
            "source",
            "updated_at",
        ]


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ["price", "created_at"]
