"""Фоновые задачи: синхронизация товаров и наполнение демо-данными."""
import random
from decimal import Decimal

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import PriceHistory, Product

# Категории и базовые цены для демо-режима (когда в магазине нет товаров)
_DEMO_CATALOG = [
    ("Электроника", "Беспроводные наушники TWS", 2490),
    ("Электроника", "Смарт-часы Pro", 5990),
    ("Электроника", "Портативная колонка 20W", 1890),
    ("Электроника", "Игровая мышь RGB", 1290),
    ("Дом и кухня", "Набор ножей 5 предметов", 3490),
    ("Дом и кухня", "Кофемолка электрическая", 1590),
    ("Дом и кухня", "Контейнеры для хранения 12 шт", 990),
    ("Одежда", "Худи оверсайз флисовое", 2190),
    ("Одежда", "Кроссовки повседневные", 3890),
    ("Одежда", "Рюкзак городской 20 л", 1790),
    ("Спорт", "Коврик для йоги 6 мм", 1190),
    ("Спорт", "Гантели 2×5 кг", 2690),
    ("Красота", "Фен ionic 2000W", 2290),
    ("Красота", "Массажёр для шеи", 1990),
    ("Дети", "Конструктор 500 деталей", 2590),
    ("Дети", "Мягкий мишка 60 см", 1390),
]


def _seed_products(count: int = 60) -> int:
    """Наполняет БД демо-товарами. Возвращает количество созданных."""
    created = 0
    for i in range(count):
        category, base_name, base_price = _DEMO_CATALOG[i % len(_DEMO_CATALOG)]
        offer_id = f"DEMO-{i + 1:04d}"
        if Product.objects.filter(offer_id=offer_id).exists():
            continue
        price = Decimal(base_price + random.randint(-200, 400))
        product = Product.objects.create(
            offer_id=offer_id,
            name=f"{base_name} (модель {i + 1})",
            category=category,
            price=price,
            old_price=price + Decimal(random.randint(100, 800)) if random.random() > 0.6 else None,
            stock=random.randint(0, 500),
            source="demo",
        )
        # первая точка в истории цены
        PriceHistory.objects.create(product=product, price=price)
        created += 1
    return created


@shared_task(name="core.tasks.seed_demo")
def seed_demo(count: int = 60) -> dict:
    """Создаёт демо-товары, если в магазине пусто."""
    created = _seed_products(count)
    return {"created": created}


@shared_task(name="core.tasks.sync_products")
def sync_products() -> dict:
    """Синхронизация товаров.

    - DEMO_MODE=true  -> гарантируем наличие демо-данных (магазин пуст).
    - DEMO_MODE=false -> тянем реальные товары из Ozon Seller API.
    """
    if settings.DEMO_MODE:
        created = _seed_products()
        # лёгкий дрейф цен, чтобы график истории «живой»
        for p in Product.objects.filter(source="demo").order_by("?")[:10]:
            delta = Decimal(random.randint(-80, 80))
            new_price = max(Decimal("100"), p.price + delta)
            p.price = new_price
            p.save(update_fields=["price", "updated_at"])
            PriceHistory.objects.create(product=p, price=new_price)
        return {"mode": "demo", "seeded": created, "at": timezone.now().isoformat()}

    # Реальный режим
    from .ozon import OzonClient

    client = OzonClient()
    if not client.configured:
        return {"mode": "ozon", "error": "Ozon API key is not configured"}

    try:
        listing = client.get_product_list()
        offer_ids = listing.get("result", {}).get("items", [])
        offer_ids = [it.get("offer_id") for it in offer_ids if it.get("offer_id")]
        if not offer_ids:
            return {"mode": "ozon", "synced": 0, "note": "no products in seller account"}

        info = client.get_product_info(offer_ids[:500])
        prices = client.get_prices(offer_ids[:500])
        price_map = {
            p.get("offer_id"): p
            for p in prices.get("result", {}).get("items", [])
        }

        synced = 0
        for item in info.get("result", []):
            offer_id = item.get("offer_id")
            if not offer_id:
                continue
            price_info = price_map.get(offer_id, {}).get("price", {})
            price = Decimal(price_info.get("price", "0") or "0") / 100  # копейки -> рубли
            old = price_info.get("old_price")
            old_price = Decimal(old) / 100 if old else None
            product, _ = Product.objects.update_or_create(
                offer_id=offer_id,
                defaults={
                    "name": item.get("name", offer_id),
                    "category": item.get("category_name", ""),
                    "price": price,
                    "old_price": old_price,
                    "stock": item.get("stocks", [{}])[0].get("present", 0)
                    if item.get("stocks")
                    else 0,
                    "source": "ozon",
                },
            )
            PriceHistory.objects.create(product=product, price=price)
            synced += 1
        return {"mode": "ozon", "synced": synced, "at": timezone.now().isoformat()}
    except Exception as exc:  # noqa: BLE001 — не роняем воркер из-за одного сбоя
        logger.exception("Ozon sync failed")
        return {"mode": "ozon", "error": str(exc)}
