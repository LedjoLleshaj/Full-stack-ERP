import { Component, OnInit, OnDestroy } from "@angular/core";
import { Sale } from "../models/sale.model";
import { SalesApiService } from "../shared/services/sales-api/sales-api.service";

@Component({
  selector: "app-sales-view",
  templateUrl: "./sales-view.component.html",
})
export class SalesViewComponent implements OnInit, OnDestroy {
  data: Sale[] = [];
  total: number = 0;
  periodicUpdate: any;

  constructor(private saleApiService: SalesApiService) {}

  ngOnInit() {
    this.fetchHistory();
    this.periodicUpdate = setInterval(() => {
      this.fetchHistory();
    }, 10000);
  }

  fetchHistory() {
    this.saleApiService.getSales().subscribe((data) => {
      this.total = data.length;
      this.data = data;
    });
  }

  ngOnDestroy() {
    clearInterval(this.periodicUpdate);
  }
}
