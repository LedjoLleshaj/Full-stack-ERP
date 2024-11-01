import { Component, EventEmitter, HostListener, Input, Output, ViewChild } from "@angular/core";
import { MatPaginatorModule } from "@angular/material/paginator";
import { MatTableModule } from "@angular/material/table";
import { MatButtonModule } from "@angular/material/button";
import { DatePipe, NgFor, NgIf } from "@angular/common";
import { MatSortModule } from "@angular/material/sort";
import { Sale } from "../../../models/sale.model";

@Component({
  selector: "app-sales-table",
  templateUrl: "./sales-table.component.html",
  standalone: true,
  imports: [MatTableModule, MatButtonModule, MatPaginatorModule, NgIf, NgFor, MatSortModule, DatePipe],
})
export class SalesTableComponent {
  columns: string[] = ["sale_id", "product", "quantity", "product_price", "sale_date", "address", "amount"];
  @Input() data: Sale[] = [];
  @Input() total: number = 0;
  @Output() nextPage: EventEmitter<any> = new EventEmitter();
  @Output() infoRental: EventEmitter<any> = new EventEmitter();
  @Output() announceSortChange: EventEmitter<any> = new EventEmitter();

  @ViewChild(MatPaginatorModule) paginator!: MatPaginatorModule;
}
