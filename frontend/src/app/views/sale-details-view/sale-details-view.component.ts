import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";

import { SalesApiService } from "src/app/shared/services/sales-api/sales-api.service";
import { CurrencyExchangeService } from "src/app/shared/services/currency-exchange/currency-exchange.service";
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

  // Exchange rate fields
  exchangeRate: number = 1;
  convertedAmount: number = 0;
  isLoadingRate: boolean = false;
  transactionCurrency: string = "LEK";
  isPayingFullRemaining: boolean = false; // Track if user wants to pay exact remaining balance

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private salesService: SalesApiService,
    private currencyService: CurrencyExchangeService,
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
          this.transactionCurrency = data.transaction.currency;
        }
        // Set default payment amount to remaining balance
        if (data.payment_summary?.remaining) {
          this.paymentAmount = data.payment_summary.remaining;
          this.convertedAmount = data.payment_summary.remaining;
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
      this.paymentCurrency = this.transactionCurrency;
      this.exchangeRate = 1;
      this.convertedAmount = this.paymentAmount;
    }
  }

  /**
   * Called when payment currency changes - fetches new exchange rate and updates amount
   * We need two rates:
   * - transactionToPayment: to convert remaining balance to payment currency (for max amount)
   * - paymentToTransaction: to convert payment amount back to transaction currency
   */
  onCurrencyChange(): void {
    if (this.paymentCurrency === this.transactionCurrency) {
      this.exchangeRate = 1;
      this.setMaxPaymentAmount();
      this.updateConvertedAmount();
      return;
    }

    this.isLoadingRate = true;
    
    // Fetch rate: transaction currency → payment currency
    // E.g., if sale is EUR and paying in LEK, get EUR→LEK rate (≈96)
    this.currencyService.getExchangeRate(this.transactionCurrency, this.paymentCurrency).subscribe({
      next: (rate) => {
        // This rate tells us: 1 EUR = X LEK
        // So to convert payment amount back to transaction currency: paymentAmount / rate
        this.exchangeRate = rate;
        this.setMaxPaymentAmount();
        this.updateConvertedAmount();
        this.isLoadingRate = false;
      },
      error: () => {
        this.snackBar.open("Nuk u arrit të merret kursi i këmbimit", "Mbyll", { duration: 3000 });
        this.exchangeRate = 1;
        this.isLoadingRate = false;
      },
    });
  }

  /**
   * Set payment amount to the maximum remaining balance in the selected currency
   */
  setMaxPaymentAmount(): void {
    const remaining = this.saleDetails?.payment_summary?.remaining || 0;
    // remaining is in transaction currency, multiply by rate to get payment currency
    // E.g., 100 EUR * 96 = 9600 LEK
    this.paymentAmount = Math.round(remaining * this.exchangeRate * 100) / 100;
    this.isPayingFullRemaining = true; // User wants to pay the full remaining balance
    this.updateConvertedAmount();
  }

  /**
   * Get maximum payment amount in the selected payment currency
   */
  getMaxPaymentAmount(): number {
    const remaining = this.saleDetails?.payment_summary?.remaining || 0;
    // remaining is in transaction currency, multiply by rate to get payment currency
    return Math.round(remaining * this.exchangeRate * 100) / 100;
  }

  /**
   * Called when payment amount changes
   */
  onAmountChange(): void {
    this.isPayingFullRemaining = false; // User manually changed amount, no longer full remaining
    this.updateConvertedAmount();
  }

  /**
   * Calculate the converted amount in transaction currency
   */
  private updateConvertedAmount(): void {
    // Payment amount is in payment currency, divide by rate to get transaction currency
    // E.g., 9600 LEK / 96 = 100 EUR
    if (this.exchangeRate > 0) {
      this.convertedAmount = this.paymentAmount / this.exchangeRate;
    } else {
      this.convertedAmount = this.paymentAmount;
    }
  }

  /**
   * Check if payment in different currency
   */
  isDifferentCurrency(): boolean {
    return this.paymentCurrency !== this.transactionCurrency;
  }

  /**
   * Get remaining balance in the selected payment currency
   */
  getRemainingInPaymentCurrency(): number {
    const remaining = this.saleDetails?.payment_summary?.remaining || 0;
    if (this.exchangeRate === 0) return remaining;
    return remaining / this.exchangeRate;
  }

  canSubmitPayment(): boolean {
    const remaining = this.saleDetails?.payment_summary?.remaining || 0;
    return (
      this.paymentAmount > 0 &&
      this.convertedAmount <= remaining + 0.01 && // Allow small rounding tolerance
      this.paymentMethod !== "" &&
      this.paymentCurrency !== "" &&
      !this.isLoadingRate
    );
  }

  submitPayment(): void {
    if (!this.canSubmitPayment()) {
      return;
    }

    this.isSubmittingPayment = true;

    const payment: any = {
      account_id: 0, // Will be auto-selected by backend based on payment method and currency
      amount: this.paymentAmount,
      currency: this.paymentCurrency,
      payment_method: this.paymentMethod,
      notes: this.paymentNotes || "", // Empty note lets backend generate a meaningful default
    };
    
    // If user clicked MAX, tell backend to pay exact remaining balance
    if (this.isPayingFullRemaining) {
      payment.pay_remaining = true;
    }

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
    const symbols: { [key: string]: string } = { 'EUR': '€', 'USD': '$', 'LEK': 'Lek' };
    return `${numAmount.toFixed(2)} ${symbols[currency] || currency}`;
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

