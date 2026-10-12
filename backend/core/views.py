from django.conf import settings
from django.db.models import Avg, Count, Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PriceHistory, Product
from .serializers import PriceHistorySerializer, ProductSerializer


@api_view(["GET"])
def health(request):
    return Response({"status": "ok", "demo_mode": settings.DEMO_MODE})


class ProductList(APIView):
    """Список товаров с фильтром по категории и поиском."""

    def get(self, request):
        qs = Product.objects.all()
        category = request.query_params.get("category")
        search = request.query_params.get("search")
        if category:
            qs = qs.filter(category=category)
        if search:
            qs = qs.filter(name__icontains=search)

        page_size = int(request.query_params.get("page_size", 50))
        page = int(request.query_params.get("page", 1))
        start = (page - 1) * page_size
        total = qs.count()
        items = qs[start : start + page_size]
        return Response(
            {
                "count": total,
                "page": page,
                "page_size": page_size,
                "results": ProductSerializer(items, many=True).data,
            }
        )


@api_view(["GET"])
def product_stats(request):
    """Агрегаты для дашборда: количество, средняя цена, суммарный остаток."""
    agg = Product.objects.aggregate(
        total=Count("id"),
        avg_price=Avg("price"),
        total_stock=Sum("stock"),
    )
    by_category = (
        Product.objects.values("category")
        .annotate(count=Count("id"), avg_price=Avg("price"))
        .order_by("-count")
    )
    return Response(
        {
            **agg,
            "avg_price": round(float(agg["avg_price"] or 0), 2),
            "by_category": [
                {"category": c["category"], "count": c["count"], "avg_price": round(float(c["avg_price"]), 2)}
                for c in by_category
            ],
        }
    )


@api_view(["GET"])
def product_history(request, pk):
    """История цен товара — для графика."""
    history = PriceHistory.objects.filter(product_id=pk).order_by("created_at")[:100]
    return Response(PriceHistorySerializer(history, many=True).data)


@api_view(["POST", "GET"])
def trigger_sync(request):
    """Ручной запуск синхронизации (в demo — пересоздаёт/дрейфует данные)."""
    from .tasks import sync_products

    result = sync_products.apply()
    return Response({"result": result.result})
