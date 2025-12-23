import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environment/environments";

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

@Injectable({
  providedIn: "root",
})
export class ReportsApiService {
  constructor(private http: HttpClient) {}

  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${environment.apiUrl}${environment.dashboardStats}`);
  }

  getDailyProfit(): Observable<DailyProfit[]> {
    return this.http.get<DailyProfit[]>(`${environment.apiUrl}${environment.dailyProfit}`);
  }

  getPaidVsUnpaid(): Observable<PaidVsUnpaidStats> {
    return this.http.get<PaidVsUnpaidStats>(`${environment.apiUrl}/paid-vs-unpaid`);
  }

  getTopProducts(): Observable<TopProduct[]> {
    return this.http.get<TopProduct[]>(`${environment.apiUrl}/top-products`);
  }
}

