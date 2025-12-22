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
        
        self.stdout.write(self.style.NOTICE("Fetching exchange rates..."))
        self.stdout.write(self.style.NOTICE("Currency mapping: LEK (database) <-> ALL (API)"))
        
        rates_updated = 0
        rates_created = 0
        errors = []

        for base_currency in self.CURRENCIES:
            try:
                # Convert to API code for the request
                api_base = self.to_api_code(base_currency)
                
                # Fetch rates from API
                response = requests.get(f"{self.API_URL}/{api_base}", timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get("result") != "success":
                    errors.append(f"API error for {base_currency} ({api_base}): {data.get('error-type', 'Unknown error')}")
                    continue

                conversion_rates = data.get("conversion_rates", {})

                # Update rates for all target currencies
                for target_currency in self.CURRENCIES:
                    if target_currency == base_currency:
                        # Set rate to 1 for same currency
                        rate = Decimal("1.000000")
                    else:
                        # Convert to API code to look up the rate
                        api_target = self.to_api_code(target_currency)
                        api_rate = conversion_rates.get(api_target)
                        
                        if api_rate is None:
                            errors.append(f"No rate found for {base_currency} -> {target_currency} (API: {api_base} -> {api_target})")
                            continue
                        rate = Decimal(str(api_rate))

                    if dry_run:
                        self.stdout.write(f"  Would set {base_currency} -> {target_currency}: {rate}")
                    else:
                        # Update or create the exchange rate using DB codes
                        obj, created = ExchangeRate.objects.update_or_create(
                            from_currency=base_currency,
                            to_currency=target_currency,
                            defaults={"rate": rate}
                        )
                        if created:
                            rates_created += 1
                        else:
                            rates_updated += 1

                self.stdout.write(self.style.SUCCESS(f"  ✓ {base_currency} ({api_base}) rates fetched"))

            except requests.RequestException as e:
                errors.append(f"Network error for {base_currency}: {str(e)}")
            except Exception as e:
                errors.append(f"Error processing {base_currency}: {str(e)}")

        # Summary
        self.stdout.write("")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes made"))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Exchange rates synchronized: {rates_created} created, {rates_updated} updated"
            ))

        if errors:
            self.stdout.write(self.style.ERROR("Errors encountered:"))
            for error in errors:
                self.stdout.write(self.style.ERROR(f"  - {error}"))
