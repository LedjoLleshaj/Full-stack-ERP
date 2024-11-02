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
import { DatePipe, NgFor, NgIf } from "@angular/common";
import { Sale } from "../../../models/sale.model";

@Component({
  selector: "app-sales-table",
  templateUrl: "./sales-table.component.html",
  standalone: true,
  imports: [MatTableModule, MatButtonModule, MatPaginatorModule, MatSortModule, NgIf, NgFor, DatePipe],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class SalesTableComponent implements AfterViewInit, OnChanges {
  columns: string[] = ["id", "product", "quantity", "product_price", "sale_date", "address", "amount"];

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
          return item.product.price;
        case "sale_date":
          return item.sale_date;
        case "address": //TODO: Add address to sale model
          return "address";
        case "amount":
          return item.product.price * item.quantity;
        default:
          return item.id;
      }
    };
    if (changes) {
      this.dataSource.data = this.data;
    }
  }
}
