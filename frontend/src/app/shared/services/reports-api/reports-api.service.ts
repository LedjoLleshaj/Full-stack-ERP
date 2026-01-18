import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environments/environment";

export interface AccountBalance {
  name: string;
  type: string;  // 'CASH' or 'BANK'
  currency: string;  // 'EUR', 'USD', 'LEK'
  balance: number;
}

export interface DashboardStats {
  revenue_today: number;
  revenue_month: number;
  profit: number;
  accounts: AccountBalance[];
  debt: number;
}

export interface DailyProfit {
  date: string;
  sales: number;
  purchases: number;
  profit: number;
}

export interface PaidVsUnpaidCategory {
  amount: number;
  count: number;
  label: string;
}

export interface PaidVsUnpaidStats {
  paid: PaidVsUnpaidCategory;
  partial: PaidVsUnpaidCategory;
  unpaid: PaidVsUnpaidCategory;
  total: {
    amount: number;
    count: number;
  };
}

export interface TopProduct {
  name: string;
  quantity: number;
}

export interface ProfitByCategory {
  name: string;
  profit: number;
  revenue: number;
  cost: number;
}

export interface TopClient {
  name: string;
  total_amount: number;
  transaction_count: number;
}

@Injectable({
  providedIn: "root",
})
export class ReportsApiService {
  constructor(private http: HttpClient) {}

  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${environment.apiUrl}${environment.dashboardStats}`);
  }

  getDailyProfit(days: number = 30): Observable<DailyProfit[]> {
    const params = days === 0 ? '?days=0' : `?days=${days}`;
    return this.http.get<DailyProfit[]>(`${environment.apiUrl}${environment.dailyProfit}${params}`);
  }

  getPaidVsUnpaid(): Observable<PaidVsUnpaidStats> {
    return this.http.get<PaidVsUnpaidStats>(`${environment.apiUrl}/paid-vs-unpaid`);
  }

  getTopProducts(): Observable<TopProduct[]> {
    return this.http.get<TopProduct[]>(`${environment.apiUrl}/top-products`);
  }

  getProfitByCategory(): Observable<ProfitByCategory[]> {
    return this.http.get<ProfitByCategory[]>(`${environment.apiUrl}/profit-by-category`);
  }

  getTopClients(): Observable<TopClient[]> {
    return this.http.get<TopClient[]>(`${environment.apiUrl}/top-clients`);
  }
}
