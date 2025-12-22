import { Component, OnInit } from "@angular/core";
import { ReportsApiService, DashboardStats } from "src/app/shared/services/reports-api/reports-api.service";

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

  constructor(private reportsService: ReportsApiService) {}

  ngOnInit() {
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
}
