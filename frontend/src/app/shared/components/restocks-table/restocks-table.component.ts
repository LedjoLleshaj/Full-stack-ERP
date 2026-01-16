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
import { DatePipe, NgIf } from "@angular/common";
import { RestockResponse } from "../../../models/restock.model";

@Component({
  selector: "app-restocks-table",
  templateUrl: "./restocks-table.component.html",
  standalone: true,
  imports: [MatTableModule, MatButtonModule, MatPaginatorModule, MatSortModule, NgIf, DatePipe, RouterModule, MatTooltipModule],
  styleUrls: ["./restocks-table.component.scss"],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class RestocksTableComponent implements AfterViewInit, OnChanges {
  columns: string[] = ["product", "quantity", "restock_price", "restock_date", "total", "payment_status"];

  @Input() data: RestockResponse[] = [];
  @Input() total: number = 0;

  constructor(private router: Router) {}

  dataSource = new MatTableDataSource<RestockResponse>();

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  ngOnChanges(changes: SimpleChanges) {
    this.dataSource.sortingDataAccessor = (item, property) => {
      switch (property) {
        case "id":
          return item.id;
        case "product":
          return item.product_info?.name || '';
        case "quantity":
          return item.quantity;
        case "restock_price":
          return parseFloat(item.restock_price);
        case "restock_date":
          return item.restock_date;
        case "total":
          return item.quantity * parseFloat(item.restock_price);
        case "payment_status":
          return item.transaction_info?.status || '';
        default:
          return item.id;
      }
    };
    if (changes) {
      this.dataSource.data = this.data;
    }
  }

  getTotal(restock: RestockResponse): number {
    return restock.quantity * parseFloat(restock.restock_price);
  }

  getCurrency(restock: RestockResponse): string {
    const currency = restock.transaction_info?.currency || 'EUR';
    switch (currency) {
      case 'EUR': return '€';
      case 'USD': return '$';
      default: return 'Lek';
    }
  }

  goToRestockDetails(restock: RestockResponse): void {
    this.router.navigate(['/restock', restock.id]);
  }
}
