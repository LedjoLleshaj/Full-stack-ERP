"""
AppConfig for ERP app.
Handles auto-sync of exchange rates on startup.
"""

from django.apps import AppConfig


class ErpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "erp"
    
    def ready(self):
        """
        Called when Django starts.
        Schedule exchange rate sync if rates are stale.
        """
        import threading
        from django.conf import settings
        
        # Only run in the main process, not in migrations or shell
        import sys
        if 'runserver' in sys.argv or 'gunicorn' in sys.modules:
            # Run in background thread to not block startup
            def sync_rates_if_stale():
                try:
                    from erp.models import ExchangeRate
                    from django.utils import timezone
                    from datetime import timedelta
                    
                    # Check if rates exist and are fresh (less than 7 days old)
                    latest_rate = ExchangeRate.objects.order_by('-last_updated').first()
                    
                    if latest_rate is None:
                        print("[ExchangeRate] No rates found. Syncing from API...")
                        should_sync = True
                    else:
                        # Make sure we compare timezone-aware datetimes
                        last_updated = latest_rate.last_updated
                        if timezone.is_naive(last_updated):
                            last_updated = timezone.make_aware(last_updated)
                        
                        if timezone.now() - last_updated > timedelta(days=7):
                            print(f"[ExchangeRate] Rates are stale (last updated: {latest_rate.last_updated}). Syncing...")
                            should_sync = True
                        else:
                            print(f"[ExchangeRate] Rates are fresh (last updated: {latest_rate.last_updated})")
                            should_sync = False
                    
                    if should_sync:
                        from django.core.management import call_command
                        call_command('sync_exchange_rates')
                        print("[ExchangeRate] Sync complete!")
                        
                except Exception as e:
                    print(f"[ExchangeRate] Auto-sync failed: {e}")
            
            # Start sync in background after a short delay (let Django fully start)
            timer = threading.Timer(5.0, sync_rates_if_stale)
            timer.daemon = True
            timer.start()
