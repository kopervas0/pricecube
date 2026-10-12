import logging

logger = logging.getLogger(__name__)

from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("products/", views.ProductList.as_view(), name="product-list"),
    path("products/stats/", views.product_stats, name="product-stats"),
    path("products/sync/", views.trigger_sync, name="trigger-sync"),
    path("products/<int:pk>/history/", views.product_history, name="product-history"),
    path("export/", views.export_report, name="export-report"),
    path("export/history/<int:pk>/", views.export_history, name="export-history"),
]
