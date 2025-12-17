import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";

import { SalesApiService } from "src/app/shared/services/sales-api/sales-api.service";
import { SaleDetails } from "src/app/models/sale.model";

@Component({
  selector: "app-sale-details-view",
  templateUrl: "./sale-details-view.component.html",
  styleUrls: ["./sale-details-view.component.scss"],
})
export class SaleDetailsViewComponent implements OnInit {
  saleId!: number;
  saleDetails: SaleDetails | null = null;
  isLoading = true;
  errorMessage = "";

  // Table columns for payments
  displayedColumns: string[] = ["payment_date", "amount", "payment_method", "currency", "notes"];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private salesService: SalesApiService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.saleId = Number(this.route.snapshot.paramMap.get("id"));
    if (this.saleId) {
      this.loadSaleDetails();
    } else {
      this.errorMessage = "ID e shitjes nuk u gjet";
      this.isLoading = false;
    }
  }

  loadSaleDetails(): void {
    this.isLoading = true;
    this.salesService.getSaleDetails(this.saleId).subscribe({
      next: (data) => {
        this.saleDetails = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error("Failed to load sale details:", err);
        this.errorMessage = err?.error?.error || "Gabim në ngarkimin e detajeve të shitjes";
        this.isLoading = false;
        this.snackBar.open(this.errorMessage, "Mbyll", { duration: 5000 });
      },
    });
  }

  getStatusClass(status: string): string {
    switch (status) {
      case "COMPLETED":
        return "status-completed";
      case "PARTIAL":
        return "status-partial";
      case "PENDING":
        return "status-pending";
      default:
        return "";
    }
  }

  getStatusLabel(status: string): string {
    switch (status) {
      case "COMPLETED":
        return "Paguar";
      case "PARTIAL":
        return "Pjesërisht";
      case "PENDING":
        return "Pa Paguar";
      default:
        return status;
    }
  }

  getPaymentMethodLabel(method: string): string {
    return method === "CASH" ? "Para në dorë" : "Kartë";
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString("sq-AL", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  formatCurrency(amount: number | string, currency: string): string {
    const numAmount = typeof amount === "string" ? parseFloat(amount) : amount;
    return `${numAmount.toFixed(2)} ${currency}`;
  }

  getPaymentProgress(): number {
    if (!this.saleDetails?.payment_summary) return 0;
    const { total_amount, total_paid } = this.saleDetails.payment_summary;
    return total_amount > 0 ? (total_paid / total_amount) * 100 : 0;
  }

  goBack(): void {
    this.router.navigate(["/sales"]);
  }

  goToClient(): void {
    if (this.saleDetails?.client?.id) {
      this.router.navigate(["/client", this.saleDetails.client.id]);
    }
  }
}
