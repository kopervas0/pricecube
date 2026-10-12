import logging

import requests

from django.conf import settings

logger = logging.getLogger(__name__)


class OzonClient:
    """Тонкий клиент Ozon Seller API.

    Работает только когда DEMO_MODE=false и заданы OZON_API_KEY / OZON_CLIENT_ID.
    """

    def __init__(self):
        self.host = settings.OZON_API_HOST.rstrip("/")
        self.headers = {
            "Client-Id": settings.OZON_CLIENT_ID,
            "Api-Key": settings.OZON_API_KEY,
            "Content-Type": "application/json",
        }

    @property
    def configured(self) -> bool:
        return bool(settings.OZON_API_KEY and settings.OZON_CLIENT_ID)

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.host}{path}"
        resp = requests.post(url, json=payload, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_product_list(self, page: int = 1, page_size: int = 100) -> dict:
        """POST /v1/product/list — список offer_id продавца."""
        return self._post(
            "/v1/product/list",
            {"filter": {"visibility": "ALL"}, "last_id": "", "limit": page_size},
        )

    def get_product_info(self, offer_ids: list[str]) -> dict:
        """POST /v3/product/info/list — детальная информация по товарам."""
        return self._post(
            "/v3/product/info/list",
            {"offer_id": offer_ids, "product_id": [], "sku": []},
        )

    def get_prices(self, offer_ids: list[str]) -> dict:
        """POST /v1/product/info/prices — актуальные цены."""
        return self._post(
            "/v1/product/info/prices",
            {"filter": {"offer_id": offer_ids, "product_id": []}, "limit": len(offer_ids)},
        )
