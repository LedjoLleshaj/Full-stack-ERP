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
  columns: string[] = ["sale_id", "product", "quantity", "product_price", "sale_date", "address", "amount"];

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
    if (changes["data"]) {
      this.dataSource.data = this.data; // Update data source whenever `data` input changes
    }
  }
}
