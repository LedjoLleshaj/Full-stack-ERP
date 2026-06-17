import {
  Component,
  Input,
  ViewChild,
  AfterViewInit,
  OnChanges,
  SimpleChanges,
  CUSTOM_ELEMENTS_SCHEMA,
} from "@angular/core";
import { MatPaginator } from "@angular/material/paginator";
import { Router } from "@angular/router";
import { RouterModule } from "@angular/router";
import { MatTableModule } from "@angular/material/table";
import { MatPaginatorModule } from "@angular/material/paginator";
import { MatSortModule } from "@angular/material/sort";
import { MatSort } from "@angular/material/sort";
import { MatTableDataSource } from "@angular/material/table";
import { MatButtonModule } from "@angular/material/button";
import { MatTooltipModule } from "@angular/material/tooltip";
import { DatePipe, NgClass, NgFor, NgIf } from "@angular/common";
import { SaleListRow } from "../../../models/sale.model";
import { SalesApiService } from "../../services/sales-api/sales-api.service";
import { AlbanianCurrencyPipe, AlbanianDatePipe, PaymentStatusPipe } from "../../pipes";

@Component({
  selector: "app-sales-table",
  templateUrl: "./sales-table.component.html",
  standalone: true,
  imports: [
    MatTableModule, MatButtonModule, MatPaginatorModule, MatSortModule,
    NgIf, DatePipe, RouterModule, MatTooltipModule,
    AlbanianCurrencyPipe, AlbanianDatePipe, PaymentStatusPipe
  ],
  styleUrls: ["./sales-table.component.scss"],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class SalesTableComponent implements AfterViewInit, OnChanges {
  columns: string[] = ["products", "item_count", "sale_date", "client", "total_amount", "payment_status"];

  @Input() data: SaleListRow[] = [];
  @Input() total: number = 0;

  constructor(
    private saleService: SalesApiService,
    private router: Router
  ) {}

  dataSource = new MatTableDataSource<SaleListRow>();

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  ngOnChanges(changes: SimpleChanges) {
    this.dataSource.sortingDataAccessor = (item, property) => {
      switch (property) {
        case "products":
          return item.products;
        case "item_count":
          return item.item_count;
        case "sale_date":
          return item.sale_date;
        case "client":
          return item.client.name;
        case "total_amount":
          return item.total_amount;
        default:
          return item.transaction_id;
      }
    };
    if (changes) {
      this.dataSource.data = this.data;
    }
  }

  /**
   * Navigate to the sale details page
   * @param row - The sale list row to view details for
   */
  goToSaleDetails(row: SaleListRow): void {
    this.router.navigate(['/sales', row.transaction_id]);
  }
}
