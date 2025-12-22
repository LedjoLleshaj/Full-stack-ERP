import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable, of, map, catchError } from "rxjs";
import { environment } from "src/environment/environments";

export interface ExchangeRatesResponse {
  rates: { [fromCurrency: string]: { [toCurrency: string]: number } };
  last_updated: string | null;
  currencies: string[];
}

export interface ExchangeRateResponse {
  from_currency: string;
  to_currency: string;
  rate: number;
  last_updated?: string;
}

export interface ConvertCurrencyResponse {
  original_amount: number;
  converted_amount: number;
  from_currency: string;
  to_currency: string;
  rate: number;
  last_updated?: string;
}

@Injectable({
  providedIn: "root",
})
export class CurrencyExchangeService {
  constructor(private http: HttpClient) {}

  /**
   * Get all exchange rates from the database
   */
  getExchangeRates(): Observable<ExchangeRatesResponse> {
    return this.http.get<ExchangeRatesResponse>(`${environment.apiUrl}/exchange-rates`).pipe(
      catchError((error) => {
        console.error("Failed to fetch exchange rates:", error);
        // Return fallback rates if API fails
        return of(this.getFallbackRates());
      })
    );
  }

  /**
   * Get a specific exchange rate between two currencies
   */
  getExchangeRate(fromCurrency: string, toCurrency: string): Observable<number> {
    if (fromCurrency.toUpperCase() === toCurrency.toUpperCase()) {
      return of(1);
    }

    return this.http
      .get<ExchangeRateResponse>(
        `${environment.apiUrl}/exchange-rate/${fromCurrency}/${toCurrency}`
      )
      .pipe(
        map((response) => response.rate),
        catchError((error) => {
          console.error("Failed to fetch exchange rate:", error);
          return of(this.getFallbackRate(fromCurrency, toCurrency));
        })
      );
  }

  /**
   * Convert an amount from one currency to another
   */
  convertCurrency(
    amount: number,
    fromCurrency: string,
    toCurrency: string
  ): Observable<ConvertCurrencyResponse> {
    if (fromCurrency.toUpperCase() === toCurrency.toUpperCase()) {
      return of({
        original_amount: amount,
        converted_amount: amount,
        from_currency: fromCurrency,
        to_currency: toCurrency,
        rate: 1,
      });
    }

    return this.http
      .post<ConvertCurrencyResponse>(`${environment.apiUrl}/convert-currency`, {
        amount,
        from_currency: fromCurrency,
        to_currency: toCurrency,
      })
      .pipe(
        catchError((error) => {
          console.error("Failed to convert currency:", error);
          const rate = this.getFallbackRate(fromCurrency, toCurrency);
          return of({
            original_amount: amount,
            converted_amount: amount * rate,
            from_currency: fromCurrency,
            to_currency: toCurrency,
            rate: rate,
          });
        })
      );
  }

  /**
   * Fallback rates in case API is unavailable
   * These are approximate rates and should be updated periodically
   */
  private getFallbackRates(): ExchangeRatesResponse {
    return {
      rates: {
        EUR: { EUR: 1, USD: 1.16, LEK: 95 },
        USD: { EUR: 0.85, USD: 1, LEK: 82 },
        LEK: { EUR: 0.013, USD: 0.012, LEK: 1 },
      },
      last_updated: null,
      currencies: ["EUR", "USD", "LEK"],
    };
  }

  /**
   * Get a specific fallback rate
   */
  private getFallbackRate(fromCurrency: string, toCurrency: string): number {
    const fallback = this.getFallbackRates();
    return fallback.rates[fromCurrency.toUpperCase()]?.[toCurrency.toUpperCase()] || 1;
  }
}
