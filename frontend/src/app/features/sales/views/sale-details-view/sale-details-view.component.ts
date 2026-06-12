import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";


import { SalesApiService } from "src/app/shared/services/sales-api/sales-api.service";
import { CurrencyExchangeService } from "src/app/shared/services/currency-exchange/currency-exchange.service";
import { ProductService } from "src/app/shared/services/product-api/product.service";
import { MatDialog } from "@angular/material/dialog";
import { SaleEditDialogComponent } from "src/app/shared/components/sale-edit-dialog/sale-edit-dialog.component";
import { DeleteConfirmationDialogComponent } from "src/app/shared/components/delete-confirmation-dialog/delete-confirmation-dialog.component";
import { SaleDetails, PaymentRequest, ReturnRequest } from "../../../../models/sale.model";
import { ReturnDialogComponent, ReturnDialogData } from 'src/app/shared/components/return-dialog/return-dialog.component';
import { PaymentApiService } from "src/app/shared/services/payment-api/payment-api.service";
import { PaymentEditDialogComponent } from "src/app/shared/components/payment-edit-dialog/payment-edit-dialog.component";
import { AuthApiService } from "src/app/shared/services/auth-api/auth-api.service";
import { InvoiceService } from "src/app/shared/services/invoice/invoice.service";

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
  displayedColumns: string[] = ["payment_date", "amount", "payment_method", "currency", "notes", "actions"];

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
    private productService: ProductService,
    private paymentService: PaymentApiService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    public authService: AuthApiService,
    private invoiceService: InvoiceService
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

  // Note: getStatusClass and getStatusLabel replaced by paymentStatus pipe

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

  downloadInvoice(): void {
    if (!this.saleDetails?.transaction) return;
    this.invoiceService.downloadInvoice(this.saleDetails.transaction.id);
    this.snackBar.open("Duke shkarkuar faturën...", "Mbyll", { duration: 3000 });
  }

  goBack(): void {
    this.router.navigate(["/sales"]);
  }

  goToClient(): void {
    if (this.saleDetails?.client?.id) {
      this.router.navigate(["/client", this.saleDetails.client.id]);
    }
  }

  onEdit(): void {
    if (!this.saleDetails) return;

    this.productService.getProducts().subscribe({
      next: (products) => {
        const dialogRef = this.dialog.open(SaleEditDialogComponent, {
          width: '600px',
          data: {
            sale: {
              ...this.saleDetails,
              prod: this.saleDetails?.product?.id,
              id: this.saleDetails?.id,
              product: this.saleDetails?.product,
              client: this.saleDetails?.client,
              quantity: this.saleDetails?.quantity,
              prod_price: this.saleDetails?.prod_price,
              payment_status: this.saleDetails?.transaction?.status,
              currency: this.saleDetails?.transaction?.currency,
              user: this.saleDetails?.user?.id || 1,
              sale_date: this.saleDetails?.sale_date
            },
            products: products,
            totalPaid: this.saleDetails?.payment_summary?.total_paid || 0
          }
        });

        dialogRef.afterClosed().subscribe(result => {
          if (result) {
            this.updateSale(result);
          }
        });
      },
      error: (err) => {
        console.error("Error loading products", err);
        this.snackBar.open("Gabim gjatë ngarkimit të produkteve", "OK", { duration: 3000 });
      }
    });
  }

  onDelete(): void {
    if (!this.saleDetails) return;

    const dialogRef = this.dialog.open(DeleteConfirmationDialogComponent, {
      width: '500px',
      data: {
        title: 'Fshi Shitjen?',
        message: `Je i sigurt që dëshiron të fshish shitjen për ${this.saleDetails.product.name}?`,
        itemDetails: {
          'Produkti': this.saleDetails.product.name,
          'Sasia': `${this.saleDetails.quantity} kg`,
          'Çmimi': this.formatCurrency(this.saleDetails.prod_price, this.saleDetails.transaction?.currency || 'EUR'),
          'Klienti': this.saleDetails.client?.name || 'Unknown'
        },
        hasPayments: (this.saleDetails.payment_summary?.total_paid || 0) > 0
      }
    });

    dialogRef.afterClosed().subscribe(confirmed => {
      if (confirmed) {
        this.deleteSale();
      }
    });
  }

  private updateSale(data: any): void {
    this.isLoading = true;
    this.salesService.updateSale(this.saleId, data).subscribe({
      next: (response) => {
        this.snackBar.open('Shitja u përditësua me sukses!', 'OK', { duration: 3000 });
        this.loadSaleDetails();
      },
      error: (error) => {
        this.isLoading = false;
        this.snackBar.open(
          error.error?.message || 'Gabim gjatë përditësimit të shitjes',
          'OK',
          { duration: 5000 }
        );
      }
    });
  }

  private deleteSale(): void {
    this.isLoading = true;
    this.salesService.deleteSale(this.saleId).subscribe({
      next: (response) => {
        this.snackBar.open(
          `Shitja u fshi! ${response.payments_reversed} pagesa u kthyen.`,
          'OK',
          { duration: 4000 }
        );
        this.goBack();
      },
      error: (error) => {
        this.isLoading = false;
        this.snackBar.open(
          error.error?.message || 'Gabim gjatë fshirjes së shitjes',
          'OK',
          { duration: 5000 }
        );
      }
    });
  }

  onEditPayment(payment: any): void {
    const dialogRef = this.dialog.open(PaymentEditDialogComponent, {
      width: '450px',
      data: {
        payment: payment,
        transactionTotal: parseFloat(this.saleDetails?.transaction?.total_amount || '0'),
        otherPaymentsTotal: (this.saleDetails?.payments || [])
          .filter((p: any) => p.id !== payment.id)
          .reduce((sum: number, p: any) => sum + (parseFloat(p.amount) || 0), 0),
        currency: this.saleDetails?.transaction?.currency || 'LEK'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.paymentService.updatePayment(payment.id, result).subscribe({
          next: () => {
            this.snackBar.open('Pagesa u përditësua me sukses', 'OK', { duration: 3000 });
            this.loadSaleDetails();
          },
          error: (err) => {
            const errorMsg = err?.error?.error || 'Gabim gjatë përditësimit të pagesës';
            this.snackBar.open(errorMsg, 'OK', { duration: 5000 });
          }
        });
      }
    });
  }

  onDeletePayment(payment: any): void {
    const dialogRef = this.dialog.open(DeleteConfirmationDialogComponent, {
      width: '400px',
      data: {
        title: 'Fshi Pagesën',
        message: `Je i sigurt që dëshiron të fshish këtë pagesë prej ${this.formatCurrency(payment.amount, payment.currency)}?`,
        itemDetails: {
          'Data': this.formatDate(payment.payment_date),
          'Shuma': this.formatCurrency(payment.amount, payment.currency),
          'Mënyra': this.getPaymentMethodLabel(payment.payment_method)
        }
      }
    });

    dialogRef.afterClosed().subscribe(confirmed => {
      if (confirmed) {
        this.paymentService.deletePayment(payment.id).subscribe({
          next: () => {
            this.snackBar.open('Pagesa u fshi me sukses', 'OK', { duration: 3000 });
            this.loadSaleDetails();
          },
          error: (err) => {
            const errorMsg = err?.error?.error || 'Gabim gjatë fshirjes së pagesës';
            this.snackBar.open(errorMsg, 'OK', { duration: 5000 });
          }
        });
      }
    });
  }

  canReturn(): boolean {
    if (!this.saleDetails?.transaction) return false;
    const status = this.saleDetails.transaction.status;
    return status !== 'CANCELLED' && status !== 'REFUNDED';
  }

  onReturn(): void {
    if (!this.saleDetails) return;

    const alreadyReturned = this.saleDetails.already_returned || {};

    const dialogData: ReturnDialogData = {
      saleId: this.saleDetails.id,
      items: [{
        sale_line_id: this.saleDetails.id,
        product_name: this.saleDetails.product.name,
        original_quantity: this.saleDetails.quantity,
        already_returned: alreadyReturned[String(this.saleDetails.product.id)] || 0,
        unit_price: this.saleDetails.prod_price,
        currency: this.saleDetails.transaction?.currency || 'EUR',
      }],
      transactionCurrency: this.saleDetails.transaction?.currency || 'EUR',
      totalPaid: this.saleDetails.payment_summary?.total_paid || 0,
      totalAmount: this.saleDetails.payment_summary?.total_amount || 0,
    };

    const dialogRef = this.dialog.open(ReturnDialogComponent, {
      width: '600px',
      data: dialogData,
    });

    dialogRef.afterClosed().subscribe((result: ReturnRequest | null) => {
      if (result) {
        this.processReturn(result);
      }
    });
  }

  private processReturn(returnRequest: ReturnRequest): void {
    this.isLoading = true;
    this.salesService.createReturn(this.saleId, returnRequest).subscribe({
      next: (response) => {
        const refundMsg = response.refund_amount > 0
          ? ` Rimbursim: ${response.refund_amount.toFixed(2)} ${this.saleDetails?.transaction?.currency || 'EUR'}`
          : '';
        this.snackBar.open(
          `Kthimi u regjistrua me sukses!${refundMsg}`,
          'OK',
          { duration: 5000 }
        );
        this.loadSaleDetails();
      },
      error: (err) => {
        this.isLoading = false;
        this.snackBar.open(
          err?.error?.error || 'Gabim gjatë regjistrimit të kthimit',
          'OK',
          { duration: 5000 }
        );
      },
    });
  }
}

