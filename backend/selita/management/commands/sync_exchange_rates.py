"""
Management command to sync exchange rates from ExchangeRate-API.
Run with: python manage.py sync_exchange_rates

This command fetches current exchange rates and stores them in the database.
Schedule this to run weekly (e.g., via cron) to keep rates updated.
"""

import requests
from decimal import Decimal
from django.core.management.base import BaseCommand
from selita.models import ExchangeRate, CURRENCY_CHOICES


class Command(BaseCommand):
    help = "Sync exchange rates from ExchangeRate-API"

    API_KEY = "d0e49dd61d7a23148afd6d38"
    API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest"

    # Currencies we support (database codes)
    CURRENCIES = [code for code, _ in CURRENCY_CHOICES]
    
    # Mapping from database currency codes to API currency codes
    # LEK is stored in DB, but API uses ALL (ISO 4217 code for Albanian Lek)
    DB_TO_API = {
        "LEK": "ALL",
        "EUR": "EUR",
        "USD": "USD",
    }
    
    # Reverse mapping from API codes to database codes
    API_TO_DB = {v: k for k, v in DB_TO_API.items()}

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without making changes",
        )

    def to_api_code(self, db_code):
        """Convert database currency code to API currency code"""
        return self.DB_TO_API.get(db_code, db_code)
    
    def to_db_code(self, api_code):
        """Convert API currency code to database currency code"""
        return self.API_TO_DB.get(api_code, api_code)

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        
        self.stdout.write(self.style.NOTICE("Fetching exchange rates with EUR as base..."))
        
        # Primary base currency for our calculations
        PRIMARY_BASE = "EUR"
        api_base = self.to_api_code(PRIMARY_BASE)
        
        try:
            # Fetch primary rates from API
            response = requests.get(f"{self.API_URL}/{api_base}", timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("result") != "success":
                self.stdout.write(self.style.ERROR(f"API error: {data.get('error-type', 'Unknown error')}"))
                return

            # These are rates from PRIMARY_BASE to other currencies
            # e.g., base_rates["USD"] = 1.08 (1 EUR = 1.08 USD)
            conversion_rates = data.get("conversion_rates", {})
            base_rates = {}
            for db_code in self.CURRENCIES:
                api_code = self.to_api_code(db_code)
                rate = conversion_rates.get(api_code)
                if rate:
                    base_rates[db_code] = Decimal(str(rate))
            
            if PRIMARY_BASE not in base_rates:
                base_rates[PRIMARY_BASE] = Decimal("1.000000")

            rates_created = 0
            rates_updated = 0

            # For every pair (A, B), calculate rate as (1/EUR->A) * (EUR->B)
            # This ensures rate(A->B) * rate(B->A) = 1 exactly (triangular consistency)
            for from_curr in self.CURRENCIES:
                for to_curr in self.CURRENCIES:
                    if from_curr == to_curr:
                        rate = Decimal("1.000000")
                    else:
                        # rate(A -> B) = (1 / rate(EUR -> A)) * rate(EUR -> B)
                        # Example: EUR->USD = 1.1, EUR->LEK = 100
                        # USD->LEK = (1/1.1) * 100 = 90.9090...
                        eur_to_from = base_rates.get(from_curr)
                        eur_to_to = base_rates.get(to_curr)
                        
                        if not eur_to_from or not eur_to_to:
                            self.stdout.write(self.style.WARNING(f"  Skipping {from_curr} -> {to_curr} (missing base rate)"))
                            continue
                            
                        rate = (Decimal("1.0") / eur_to_from) * eur_to_to
                        # Quantize to 6 decimal places as per model
                        rate = rate.quantize(Decimal("0.000001"))

                    if dry_run:
                        self.stdout.write(f"  Would set {from_curr} -> {to_curr}: {rate}")
                    else:
                        obj, created = ExchangeRate.objects.update_or_create(
                            from_currency=from_curr,
                            to_currency=to_curr,
                            defaults={"rate": rate}
                        )
                        if created: rates_created += 1
                        else: rates_updated += 1

            if not dry_run:
                self.stdout.write(self.style.SUCCESS(
                    f"Exchange rates synchronized: {rates_created} created, {rates_updated} updated"
                ))
            else:
                self.stdout.write(self.style.WARNING("DRY RUN - No changes made"))

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Network error: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
