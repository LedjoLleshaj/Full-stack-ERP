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
import { MatTableModule } from "@angular/material/table";
import { MatPaginatorModule } from "@angular/material/paginator";
import { MatSortModule } from "@angular/material/sort";
import { MatSort } from "@angular/material/sort";
import { MatTableDataSource } from "@angular/material/table";
import { MatButtonModule } from "@angular/material/button";
import { DatePipe, NgClass, NgFor, NgIf } from "@angular/common";
import { Sale } from "../../../models/sale.model";

@Component({
  selector: "app-sales-table",
  templateUrl: "./sales-table.component.html",
  standalone: true,
  imports: [MatTableModule, MatButtonModule, MatPaginatorModule, MatSortModule, NgIf, NgFor, DatePipe, NgClass],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class SalesTableComponent implements AfterViewInit, OnChanges {
  columns: string[] = ["product", "quantity", "product_price", "sale_date", "client", "address", "amount", "is_paid"];

  @Input() data: Sale[] = [];
  @Input() total: number = 0;

  dataSource = new MatTableDataSource<Sale>();

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
          return item.product.name;
        case "quantity":
          return item.quantity;
        case "product_price":
          return item.prod_price;
        case "sale_date":
          return item.sale_date;
        case "client":
          return item.client.name;
        case "address": //TODO: Add address to sale model
          return "address";
        case "amount":
          return item.prod_price * item.quantity;
        default:
          return item.id;
      }
    };
    if (changes) {
      this.dataSource.data = this.data;
    }
  }
}
