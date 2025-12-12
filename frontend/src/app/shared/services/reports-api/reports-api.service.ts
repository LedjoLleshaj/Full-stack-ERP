import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environment/environments";

export interface DashboardStats {
  revenue_today: number;
  revenue_month: number;
  profit: number;
  cash_balance: number;
  bank_balance: number;
  debt: number;
}

@Injectable({
  providedIn: "root",
})
export class ReportsApiService {
  constructor(private http: HttpClient) {}

  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${environment.apiUrl}${environment.dashboardStats}`);
  }
}
