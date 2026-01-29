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
import { Sale, SaleResponse } from "../../../models/sale.model";
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
  columns: string[] = ["product", "quantity", "product_price", "sale_date", "client", "address", "amount", "payment_status"];

  @Input() data: SaleResponse[] = [];
  @Input() total: number = 0;

  constructor(
    private saleService: SalesApiService,
    private router: Router
  ) {}

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
    // ⚡ TODO: Implement payment dialog to collect payment details
    // For now, this functionality is disabled until we add a payment form
    console.log("Payment functionality requires payment details (amount, account, method)");
    console.log("Sale ID:", sale.id, "Transaction status:", sale.payment_status);
    
    /* Example implementation:
    const payment = {
      account_id: 1,
      amount: sale.prod_price * sale.quantity,
      currency: "EUR",
      payment_method: "CASH",
      notes: "Payment via sales table"
    };
    
    this.saleService.paySale(sale.id, payment).subscribe(
      (response) => {
        console.log("Payment added", response);
        // Update the sale's payment status in the table
        this.dataSource.data = this.dataSource.data.map((s) =>
          s.id === sale.id ? { ...s, payment_status: response.transaction_status } : s
        );
      },
      (error) => {
        console.error("Error adding payment", error);
      }
    );
    */
  }

  /**
   * Navigate to the sale details page
   * @param sale - The sale to view details for
   */
  goToSaleDetails(sale: SaleResponse): void {
    this.router.navigate(['/sale', sale.id]);
  }
}
