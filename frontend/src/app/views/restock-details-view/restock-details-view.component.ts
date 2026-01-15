import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";

import { SupplierService } from "src/app/shared/services/suppliers-api/supplier.service";
import { CurrencyExchangeService } from "src/app/shared/services/currency-exchange/currency-exchange.service";

interface RestockDetails {
  id: number;
  restock_date: string;
  quantity: number;
  restock_price: string;
  product_info: {
    id: number;
    name: string;
    category: string;
    price: string;
  };
  transaction_info: {
    id: number;
    status: string;
    total_amount: string;
    currency: string;
    supplier?: number;
  };
  payments: Payment[];
}

interface Payment {
  id: number;
  payment_date: string;
  amount: string;
  currency: string;
  payment_method: string;
  notes: string;
  original_amount?: string;
  original_currency?: string;
}

interface Supplier {
  id?: number;
  firstname: string;
  lastname: string;
  email?: string;
  phone?: string;
  address?: string;
}

@Component({
  selector: "app-restock-details-view",
  templateUrl: "./restock-details-view.component.html",
  styleUrls: ["./restock-details-view.component.scss"],
})
export class RestockDetailsViewComponent implements OnInit {
  restockId!: number;
  restockDetails: RestockDetails | null = null;
  supplier: Supplier | null = null;
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
  paymentCurrency: string = "EUR";
  currencies: string[] = ["LEK", "EUR", "USD"];
  paymentNotes: string = "";

  // Exchange rate fields
  exchangeRate: number = 1;
  convertedAmount: number = 0;
  isLoadingRate: boolean = false;
  transactionCurrency: string = "EUR";
  isPayingFullRemaining: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private supplierService: SupplierService,
    private currencyService: CurrencyExchangeService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.restockId = Number(this.route.snapshot.paramMap.get("id"));
    if (this.restockId) {
      this.loadRestockDetails();
    } else {
      this.errorMessage = "ID e furnizimit nuk u gjet";
      this.isLoading = false;
    }
  }

  loadRestockDetails(): void {
    this.isLoading = true;
    this.supplierService.getRestockDetails(this.restockId).subscribe({
      next: (data) => {
        this.restockDetails = data;
        this.isLoading = false;
        // Set default payment currency to match transaction currency
        if (data.transaction_info?.currency) {
          this.paymentCurrency = data.transaction_info.currency;
          this.transactionCurrency = data.transaction_info.currency;
        }
        // Calculate remaining and set default amount
        const remaining = this.getRemainingBalance();
        if (remaining > 0) {
          this.paymentAmount = remaining;
          this.convertedAmount = remaining;
        }
        // Load supplier info
        if (data.transaction_info?.supplier) {
          this.loadSupplierInfo(data.transaction_info.supplier);
        }
      },
      error: (err) => {
        console.error("Failed to load restock details:", err);
        this.errorMessage = err?.error?.error || "Gabim në ngarkimin e detajeve të furnizimit";
        this.isLoading = false;
        this.snackBar.open(this.errorMessage, "Mbyll", { duration: 5000 });
      },
    });
  }

  loadSupplierInfo(supplierId: number): void {
    this.supplierService.getSupplier(supplierId).subscribe({
      next: (supplier) => {
        this.supplier = supplier;
      },
      error: (err) => {
        console.error("Failed to load supplier info:", err);
      },
    });
  }

  // Payment summary calculations
  getTotalAmount(): number {
    if (!this.restockDetails?.transaction_info) return 0;
    return parseFloat(this.restockDetails.transaction_info.total_amount) || 0;
  }

  getTotalPaid(): number {
    if (!this.restockDetails?.payments) return 0;
    return this.restockDetails.payments.reduce((sum, p) => sum + (parseFloat(p.amount) || 0), 0);
  }

  getRemainingBalance(): number {
    return Math.max(0, this.getTotalAmount() - this.getTotalPaid());
  }

  hasRemainingBalance(): boolean {
    return this.getRemainingBalance() > 0;
  }

  getPaymentProgress(): number {
    const total = this.getTotalAmount();
    if (total <= 0) return 0;
    return (this.getTotalPaid() / total) * 100;
  }

  // Payment form methods
  togglePaymentForm(): void {
    this.showPaymentForm = !this.showPaymentForm;
    if (this.showPaymentForm) {
      this.paymentAmount = this.getRemainingBalance();
      this.paymentCurrency = this.transactionCurrency;
      this.exchangeRate = 1;
      this.convertedAmount = this.paymentAmount;
    }
  }

  onCurrencyChange(): void {
    if (this.paymentCurrency === this.transactionCurrency) {
      this.exchangeRate = 1;
      this.setMaxPaymentAmount();
      this.updateConvertedAmount();
      return;
    }

    this.isLoadingRate = true;
    this.currencyService.getExchangeRate(this.transactionCurrency, this.paymentCurrency).subscribe({
      next: (rate) => {
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

  setMaxPaymentAmount(): void {
    const remaining = this.getRemainingBalance();
    this.paymentAmount = Math.round(remaining * this.exchangeRate * 100) / 100;
    this.isPayingFullRemaining = true;
    this.updateConvertedAmount();
  }

  getMaxPaymentAmount(): number {
    const remaining = this.getRemainingBalance();
    return Math.round(remaining * this.exchangeRate * 100) / 100;
  }

  onAmountChange(): void {
    this.isPayingFullRemaining = false;
    this.updateConvertedAmount();
  }

  private updateConvertedAmount(): void {
    if (this.exchangeRate > 0) {
      this.convertedAmount = this.paymentAmount / this.exchangeRate;
    } else {
      this.convertedAmount = this.paymentAmount;
    }
  }

  isDifferentCurrency(): boolean {
    return this.paymentCurrency !== this.transactionCurrency;
  }

  canSubmitPayment(): boolean {
    const remaining = this.getRemainingBalance();
    return (
      this.paymentAmount > 0 &&
      this.convertedAmount <= remaining + 0.01 &&
      this.paymentMethod !== "" &&
      this.paymentCurrency !== "" &&
      !this.isLoadingRate
    );
  }

  submitPayment(): void {
    if (!this.canSubmitPayment() || !this.restockDetails) {
      return;
    }

    this.isSubmittingPayment = true;

    const payment: any = {
      transaction_id: this.restockDetails.transaction_info.id,
      account_id: 0,
      amount: this.paymentAmount,
      currency: this.paymentCurrency,
      payment_method: this.paymentMethod,
      notes: this.paymentNotes || `Pagesë për furnizimin #${this.restockId}`,
    };

    if (this.isPayingFullRemaining) {
      payment.pay_remaining = true;
    }

    this.supplierService.payRestock(this.restockId, payment).subscribe({
      next: () => {
        this.snackBar.open("Pagesa u regjistrua me sukses!", "Mbyll", { duration: 3000 });
        this.isSubmittingPayment = false;
        this.showPaymentForm = false;
        this.paymentNotes = "";
        this.loadRestockDetails();
      },
      error: (err) => {
        console.error("Failed to submit payment:", err);
        const errorMsg = err?.error?.error || "Gabim në regjistrimin e pagesës";
        this.snackBar.open(errorMsg, "Mbyll", { duration: 5000 });
        this.isSubmittingPayment = false;
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

  goBack(): void {
    if (this.supplier) {
      this.router.navigate(["/supplier", this.supplier.id]);
    } else {
      this.router.navigate(["/suppliers"]);
    }
  }

  goToSupplier(): void {
    if (this.supplier?.id) {
      this.router.navigate(["/supplier", this.supplier.id]);
    }
  }
}
