"""
Management command to check inventory levels against product reorder levels.

Intended to run on a schedule (cron / scheduled task). Logs a warning for
every active product whose on-hand stock is at or below its reorder level.
"""

import logging

from django.core.management.base import BaseCommand

from erp.services.inventory_service import InventoryService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Warn about products at or below their reorder level."

    def handle(self, *args, **options):
        products = list(InventoryService.get_low_stock_products())

        for product in products:
            message = (
                f"Low stock: '{product.name}' has {product.stock} on hand "
                f"(reorder level: {product.reorder_level}, "
                f"suggested reorder quantity: {product.reorder_quantity})"
            )
            logger.warning(message)
            self.stdout.write(self.style.WARNING(message))

        self.stdout.write(f"{len(products)} product(s) at or below reorder level.")
