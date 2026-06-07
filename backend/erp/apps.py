"""
AppConfig for ERP app.
Handles auto-sync of exchange rates on startup.
"""

from django.apps import AppConfig


class ErpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "erp"
    
    def ready(self):
        import os
        if os.environ.get("RUN_FX_SYNC") != "1":
            return

        import threading

        def sync_rates_if_stale():
            try:
                from datetime import timedelta

                from django.utils import timezone

                from erp.models import ExchangeRate

                latest_rate = ExchangeRate.objects.order_by('-last_updated').first()

                if latest_rate is None:
                    should_sync = True
                else:
                    last_updated = latest_rate.last_updated
                    if timezone.is_naive(last_updated):
                        last_updated = timezone.make_aware(last_updated)
                    should_sync = timezone.now() - last_updated > timedelta(days=7)

                if should_sync:
                    from django.core.management import call_command
                    call_command('sync_exchange_rates')
            except Exception as e:
                print(f"[ExchangeRate] Auto-sync failed: {e}")

        timer = threading.Timer(5.0, sync_rates_if_stale)
        timer.daemon = True
        timer.start()
