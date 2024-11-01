import { Component, Output } from "@angular/core";

import { PageEvent } from "@angular/material/paginator";
import { MatDialog } from "@angular/material/dialog";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { ActivatedRoute } from "@angular/router";
import { LiveAnnouncer } from "@angular/cdk/a11y";
import { LOCAL_STORAGE_KEYS } from "../shared/constants";
import { Sale } from "../models/sale.model";
import { SalesApiService } from "../shared/services/sales-api/sales-api.service";

@Component({
  selector: "app-sales-view",
  templateUrl: "./sales-view.component.html",
  providers: [MatProgressSpinnerModule],
})
export class SalesViewComponent {
  data: Sale[];
  total: number;
  periodicUpdate: any;

  constructor(
    private saleApiService: SalesApiService,
    private dialog: MatDialog,
    private _liveAnnouncer: LiveAnnouncer
  ) {}

  ngOnInit() {
    this.fetchHistory();
    //this.fetchStats();
    this.periodicUpdate = setInterval(() => {
      this.fetchHistory();
      //this.fetchStats();
    }, 10000);
  }

  fetchHistory() {
    this.saleApiService.getSales().subscribe((data) => {
      this.total = data.length;
      this.data = data;
    });
  }

  // fetchStats() {
  //   this.saleApiService.getSalesStats().subscribe((data) => {
  //     this.cardData = [
  //       {
  //         icon: "upcoming",
  //         stat: String(data.getUser.rental_stats.current_rentals),
  //         description: "Rentals in progress",
  //       },
  //       {
  //         icon: "wallet",
  //         stat: String(data.getUser.rental_stats.total_amount) + " €",
  //         description: "Total spendings",
  //       },
  //       {
  //         icon: "category",
  //         stat: data.getUser.rental_stats?.most_frequent_category?.name,
  //         description: "Favorite category",
  //       },
  //       {
  //         icon: "timeline",
  //         stat: String(data.getUser.rental_stats.total_rentals),
  //         description: "Total rentals",
  //       },
  //     ];
  //   });
  // }

  nextPage(event: PageEvent) {
    // this.filter.page = event.pageIndex + 1;
    // this.filter.itemsPerPage = event.pageSize;
    this.fetchHistory();
  }

  // infoRental(sale: Sale) {
  //   this.saleApiService.getRental(rental.rental_id).subscribe((rental) => {
  //     this.dialog.open(RentalDetailsDialogComponent, {
  //       width: "532px",
  //       data: rental,
  //     });
  //   });
  // }

  announceSortChange(sort: any) {
    this.fetchHistory();

    if (sort.direction) {
      this._liveAnnouncer.announce(`Sorted ${sort.direction}ending`);
    } else {
      this._liveAnnouncer.announce("Sorting cleared");
    }
  }

  ngOnDestroy() {
    clearInterval(this.periodicUpdate);
  }
}
