import { Component, OnInit } from "@angular/core";
import { ReportsApiService, DashboardStats } from "src/app/shared/services/reports-api/reports-api.service";

@Component({
  selector: "app-reports-view",
  templateUrl: "./reports-view.component.html",
})
export class ReportsViewComponent implements OnInit {
  stats: DashboardStats = {
    revenue_today: 0,
    revenue_month: 0,
    profit: 0,
    cash_balance: 0,
    bank_balance: 0,
    debt: 0
  };

  constructor(private reportsService: ReportsApiService) {}

  ngOnInit() {
    this.reportsService.getDashboardStats().subscribe(data => {
      this.stats = data;
    });
  }
}
