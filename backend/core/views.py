import io

import pandas as pd
from django.conf import settings
from django.db.models import Avg, Count, Sum
from django.http import HttpResponse
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


# ===== Экспорт отчётов (pandas) =====

_REPORT_COLUMNS = {
    "offer_id": "Артикул",
    "name": "Название",
    "category": "Категория",
    "price": "Цена, ₽",
    "old_price": "Старая цена, ₽",
    "stock": "Остаток, шт",
    "source": "Источник",
}


def _build_dataframe():
    """Собирает отчёт по товарам в DataFrame с русскими заголовками."""
    rows = list(
        Product.objects.values(*_REPORT_COLUMNS.keys()).order_by("category", "offer_id")
    )
    df = pd.DataFrame(rows, columns=list(_REPORT_COLUMNS.keys()))
    df = df.rename(columns=_REPORT_COLUMNS)
    # агрегат в конец — удобно видеть итог в отчёте
    return df


@api_view(["GET"])
def export_report(request):
    """Экспорт отчёта по товарам.

    GET /api/export/?format=csv|xlsx  -> файл-отчёт.
    """
    fmt = (request.query_params.get("format") or "csv").lower()
    df = _build_dataframe()

    if fmt == "xlsx":
        buffer = io.BytesIO()
        # pandas engine для Excel
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Товары")
            # авто-ширина колонок, чтобы отчёт читался
            worksheet = writer.sheets["Товары"]
            for idx, col in enumerate(df.columns, start=1):
                width = max(df[col].astype(str).str.len().max(), len(str(col))) + 2
                worksheet.column_dimensions[
                    worksheet.cell(row=1, column=idx).column_letter
                ].width = min(int(width), 60)
        data = buffer.getvalue()
        response = HttpResponse(
            data,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        filename = "pricecube_report.xlsx"
    else:
        # UTF-8 с BOM — чтобы Excel корректно открыл русские буквы
        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        response = HttpResponse(csv_data, content_type="text/csv; charset=utf-8")
        filename = "pricecube_report.csv"

    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@api_view(["GET"])
def export_history(request, pk):
    """Экспорт истории цен конкретного товара (CSV)."""
    history = PriceHistory.objects.filter(product_id=pk).order_by("created_at")
    rows = [{"created_at": h.created_at.isoformat(), "price": float(h.price)} for h in history]
    df = pd.DataFrame(rows, columns=["created_at", "price"])
    df = df.rename(columns={"created_at": "Время", "price": "Цена, ₽"})
    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    response = HttpResponse(csv_data, content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="price_history_{pk}.csv"'
    return response
