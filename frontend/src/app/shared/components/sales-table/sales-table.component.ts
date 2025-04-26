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
import { Sale, SaleResponse } from "../../../models/sale.model";
import { SalesApiService } from "../../services/sales-api/sales-api.service";

@Component({
  selector: "app-sales-table",
  templateUrl: "./sales-table.component.html",
  standalone: true,
  imports: [MatTableModule, MatButtonModule, MatPaginatorModule, MatSortModule, NgIf, DatePipe],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class SalesTableComponent implements AfterViewInit, OnChanges {
  columns: string[] = ["product", "quantity", "product_price", "sale_date", "client", "address", "amount", "is_paid"];

  @Input() data: SaleResponse[] = [];
  @Input() total: number = 0;

  constructor(private saleService: SalesApiService) {}

  dataSource = new MatTableDataSource<SaleResponse>();

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

  markAsPaid(sale: any): void {
    // Replace with your actual API service
    console.log("Marking as paid", sale.id);
    this.saleService.paySale(sale.id).subscribe(
      (response) => {
        console.log("Sale marked as paid", response);
        // Optionally, refresh the data or update the UI
        this.dataSource.data = this.dataSource.data.map((s) => (s.id === sale.id ? { ...s, is_paid: true } : s));
      },
      (error) => {
        console.error("Error marking sale as paid", error);
      }
    );
  }
}
