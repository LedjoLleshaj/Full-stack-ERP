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

import { BaseApiService } from "../base-api.service";

@Injectable({
  providedIn: "root",
})
export class ReportsApiService extends BaseApiService {
  constructor(http: HttpClient) {
    super(http);
  }

  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.apiUrl}${environment.dashboardStats}`);
  }

  getDailyProfit(days: number = 30): Observable<DailyProfit[]> {
    const params = this.createParams({ days });
    return this.http.get<DailyProfit[]>(`${this.apiUrl}${environment.dailyProfit}`, { params });
  }

  getPaidVsUnpaid(): Observable<PaidVsUnpaidStats> {
    return this.http.get<PaidVsUnpaidStats>(`${this.apiUrl}/paid-vs-unpaid`);
  }

  getTopProducts(): Observable<TopProduct[]> {
    return this.http.get<TopProduct[]>(`${this.apiUrl}/top-products`);
  }

  getProfitByCategory(): Observable<ProfitByCategory[]> {
    return this.http.get<ProfitByCategory[]>(`${this.apiUrl}/profit-by-category`);
  }

  getTopClients(): Observable<TopClient[]> {
    return this.http.get<TopClient[]>(`${this.apiUrl}/top-clients`);
  }
}
