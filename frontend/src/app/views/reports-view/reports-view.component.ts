import { Component, OnInit } from "@angular/core";
import { ReportsApiService, DashboardStats } from "src/app/shared/services/reports-api/reports-api.service";
import { CurrencyExchangeService, ExchangeRatesResponse } from "src/app/shared/services/currency-exchange/currency-exchange.service";

@Component({
  selector: "app-reports-view",
  templateUrl: "./reports-view.component.html",
  styleUrls: ["./reports-view.component.scss"],
})
export class ReportsViewComponent implements OnInit {
  stats: DashboardStats = {
    revenue_today: 0,
    revenue_month: 0,
    profit: 0,
    accounts: [],
    debt: 0
  };

  exchangeRates: { [from: string]: { [to: string]: number } } = {};

  constructor(
    private reportsService: ReportsApiService,
    private currencyService: CurrencyExchangeService
  ) {}

  ngOnInit() {
    // Load exchange rates first, then load stats
    this.currencyService.getExchangeRates().subscribe(data => {
      this.exchangeRates = data.rates;
    });

    this.reportsService.getDashboardStats().subscribe(data => {
      this.stats = data;
    });
  }

  get cashAccounts() {
    return this.stats.accounts.filter(a => a.type === 'CASH');
  }

  get bankAccounts() {
    return this.stats.accounts.filter(a => a.type === 'BANK');
  }

  get cashTotalEur(): number {
    return this.calculateTotalInEur(this.cashAccounts);
  }

  get bankTotalEur(): number {
    return this.calculateTotalInEur(this.bankAccounts);
  }

  private calculateTotalInEur(accounts: { currency: string; balance: number }[]): number {
    let total = 0;
    for (const account of accounts) {
      if (account.currency === 'EUR') {
        total += account.balance;
      } else {
        const rate = this.exchangeRates[account.currency]?.['EUR'] || 1;
        total += account.balance * rate;
      }
    }
    return total;
  }
}
