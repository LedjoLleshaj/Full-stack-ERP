import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";

import { SalesApiService } from "src/app/shared/services/sales-api/sales-api.service";
import { SaleDetails, PaymentRequest } from "src/app/models/sale.model";

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

  // Payment form fields
  showPaymentForm = false;
  isSubmittingPayment = false;
  paymentAmount: number = 0;
  paymentMethod: string = "CASH";
  paymentMethods: string[] = ["CASH", "CARD"];
  paymentCurrency: string = "LEK";
  currencies: string[] = ["LEK", "EUR", "USD"];
  paymentNotes: string = "";

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
        // Set default payment currency to match transaction currency
        if (data.transaction?.currency) {
          this.paymentCurrency = data.transaction.currency;
        }
        // Set default payment amount to remaining balance
        if (data.payment_summary?.remaining) {
          this.paymentAmount = data.payment_summary.remaining;
        }
      },
      error: (err) => {
        console.error("Failed to load sale details:", err);
        this.errorMessage = err?.error?.error || "Gabim në ngarkimin e detajeve të shitjes";
        this.isLoading = false;
        this.snackBar.open(this.errorMessage, "Mbyll", { duration: 5000 });
      },
    });
  }

  // Payment form methods
  togglePaymentForm(): void {
    this.showPaymentForm = !this.showPaymentForm;
    if (this.showPaymentForm && this.saleDetails?.payment_summary?.remaining) {
      this.paymentAmount = this.saleDetails.payment_summary.remaining;
    }
  }

  canSubmitPayment(): boolean {
    return (
      this.paymentAmount > 0 &&
      this.paymentAmount <= (this.saleDetails?.payment_summary?.remaining || 0) &&
      this.paymentMethod !== "" &&
      this.paymentCurrency !== ""
    );
  }

  submitPayment(): void {
    if (!this.canSubmitPayment()) {
      return;
    }

    this.isSubmittingPayment = true;

    const payment: PaymentRequest = {
      account_id: 0, // Will be auto-selected by backend based on payment method and currency
      amount: this.paymentAmount,
      currency: this.paymentCurrency,
      payment_method: this.paymentMethod as "CASH" | "CARD",
      notes: this.paymentNotes || `Pagesë për shitjen #${this.saleId}`,
    };

    this.salesService.paySale(this.saleId, payment).subscribe({
      next: (response) => {
        this.snackBar.open("Pagesa u regjistrua me sukses!", "Mbyll", { duration: 3000 });
        this.isSubmittingPayment = false;
        this.showPaymentForm = false;
        this.paymentNotes = "";
        // Reload sale details to show updated payment info
        this.loadSaleDetails();
      },
      error: (err) => {
        console.error("Failed to submit payment:", err);
        const errorMsg = err?.error?.error || "Gabim në regjistrimin e pagesës";
        this.snackBar.open(errorMsg, "Mbyll", { duration: 5000 });
        this.isSubmittingPayment = false;
      },
    });
  }

  hasRemainingBalance(): boolean {
    return (this.saleDetails?.payment_summary?.remaining || 0) > 0;
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
    return method === "CASH" ? "Cash" : "Kartë";
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
