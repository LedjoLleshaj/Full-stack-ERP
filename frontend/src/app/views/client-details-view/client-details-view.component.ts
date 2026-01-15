import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";

import { Client } from "src/app/models/client.model";
import { Product } from "src/app/models/product.model";
import { ClientService } from "src/app/shared/services/clients-api/client.service";
import { ProductService } from "src/app/shared/services/product-api/product.service";
import { SalesApiService } from "src/app/shared/services/sales-api/sales-api.service";
import { CurrencyExchangeService } from "src/app/shared/services/currency-exchange/currency-exchange.service";
import { Router } from "@angular/router";

@Component({
  selector: "app-client-details-view",
  templateUrl: "./client-details-view.component.html",
  styleUrls: ["./client-details-view.component.scss"],
})
export class ClientDetailsViewComponent implements OnInit {
  client: Client | undefined;
  clientId!: number;
  searchText = "";
  availableProducts: Product[] = [];
  selectedProduct: Product | null = null;
  saleQuantity: number = 1;
  salePrice: number = 0;
  basePriceEUR: number = 0; // Base product price in EUR for conversion
  isPaid: boolean = true;
  currentUserId: number = 1; // ⚡ TODO: Get from auth service
  lastSoldPrice: number | null = null;
  lastSoldCurrency: string | null = null; // Currency of the last sale

  // Payment method and currency options
  paymentMethod: string = "CASH";
  paymentMethods: string[] = ["CASH", "CARD"];
  currency: string = "EUR"; // Default to EUR since product prices are in EUR
  currencies: string[] = ["EUR", "USD", "LEK"];

  // Recent sales
  recentSales: any[] = [];
  isLoadingSales = false;
  salesColumns = ['date', 'product_name', 'quantity', 'price', 'status'];

  constructor(
    private route: ActivatedRoute,
    private clientService: ClientService,
    private productService: ProductService,
    private saleService: SalesApiService,
    private snackBar: MatSnackBar,
    private currencyExchange: CurrencyExchangeService,
    private router: Router
  ) {}

  ngOnInit() {
    this.clientId = Number(this.route.snapshot.paramMap.get("id"));
    if (this.clientId) {
      this.loadClient(this.clientId);
      this.loadClientSales(this.clientId);
    }
    this.fetchProducts();
  }

  private loadClient(clientId: number): void {
    this.clientService.getClientById(clientId).subscribe({
      next: (data: Client) => {
        this.client = data;
      },
      error: (err) => {
        console.error("Failed to load client:", err);
        this.snackBar.open("Gabim ne ngarkimin e klientit", "Mbyll", { duration: 3000 });
      },
    });
  }

  private loadClientSales(clientId: number): void {
    this.isLoadingSales = true;
    this.clientService.getClientSales(clientId).subscribe({
      next: (data: any[]) => {
        // Filter to only unpaid sales (PENDING or PARTIAL), take last 10
        this.recentSales = data
          .filter(sale => sale.payment_status !== 'COMPLETED')
          .slice(0, 10);
        this.isLoadingSales = false;
      },
      error: (err) => {
        console.error('Failed to load client sales:', err);
        this.isLoadingSales = false;
      }
    });
  }

  fetchProducts(): void {
    this.productService.getProducts().subscribe({
      next: (products) => {
        this.availableProducts = products.filter((product) => product.disponibility > 0);
      },
      error: (err) => {
        console.error("Failed to fetch products:", err);
        this.snackBar.open("Gabim ne ngarkimin e produkteve", "Mbyll", { duration: 3000 });
      },
    });
  }
  enforceMax(event: any) {
    const input = event.target as HTMLInputElement;
    const max = this.selectedProduct?.disponibility ?? 0;

    if (+input.value > max) {
      input.value = String(max);
      this.saleQuantity = max; // keep ngModel in sync
    }

    // Prevent typing more digits than the max allows
    if (input.value.length > max.toString().length) {
      input.value = input.value.slice(0, max.toString().length);
    }
  }

  filteredProducts(): Product[] {
    if (!this.searchText) {
      return this.availableProducts;
    }
    return this.availableProducts.filter((p) => p.name.toLowerCase().includes(this.searchText.toLowerCase()));
  }

  onProductSelect(event: any): void {
    const product = event.option.value;
    this.selectedProduct = product;
    if (this.selectedProduct) {
      this.salePrice = this.selectedProduct.price;
      this.basePriceEUR = this.selectedProduct.price; // Store base price for currency conversion
      this.currency = "EUR"; // Reset to EUR when selecting new product
      this.saleQuantity = 1;
      // Update searchText to show the selected product name
      this.searchText = this.selectedProduct.name;

      // Fetch last sold price
      if (this.selectedProduct.id) {
        this.saleService.getLastSoldPrice(this.clientId, this.selectedProduct.id).subscribe({
          next: (response) => {
            this.lastSoldPrice = response.price;
            this.lastSoldCurrency = response.currency;
          },
          error: (err) => {
            console.error("Failed to fetch last sold price:", err);
            this.lastSoldPrice = null;
            this.lastSoldCurrency = null;
          },
        });
      }
    }
  }

  /**
   * Called when currency dropdown changes - convert price from EUR to selected currency
   */
  onCurrencyChange(): void {
    if (!this.selectedProduct || this.basePriceEUR === 0) return;

    if (this.currency === "EUR") {
      // Reset to base EUR price
      this.salePrice = this.basePriceEUR;
    } else {
      // Convert EUR to selected currency
      this.currencyExchange.getExchangeRate("EUR", this.currency).subscribe({
        next: (rate) => {
          this.salePrice = Math.round(this.basePriceEUR * rate * 100) / 100;
        },
        error: () => {
          this.snackBar.open("Gabim në marrjen e kursit të këmbimit", "Mbyll", { duration: 3000 });
        },
      });
    }
  }

  displayProduct(product: Product | null): string {
    // This function is used for displaying in the input field
    return product ? product.name : "";
  }

  getTotal(): number {
    return this.salePrice * this.saleQuantity;
  }

  canCreateSale(): boolean {
    return (
      this.selectedProduct != null &&
      this.saleQuantity > 0 &&
      this.saleQuantity <= this.selectedProduct.disponibility &&
      this.salePrice > 0
    );
  }

  createSale(): void {
    if (!this.canCreateSale() || !this.selectedProduct) {
      return;
    }

    const total = this.getTotal();

    const newSale: any = {
      prod: this.selectedProduct.id,
      prod_price: this.salePrice,
      quantity: this.saleQuantity,
      user: this.currentUserId,
      client_id: this.clientId, // Changed from 'client'
      currency: this.currency,
    };

    // If isPaid is true, add payment data
    if (this.isPaid) {
      newSale.payment = {
        amount: total,
        currency: this.currency,
        payment_method: this.paymentMethod,
        notes: `Payment for sale of ${this.saleQuantity} ${this.selectedProduct.name}`,
      };
    }

    this.saleService.createSale(newSale).subscribe({
      next: (response) => {
        console.log("Sale created successfully:", response);
        const statusMsg = response.transaction_status === 'COMPLETED' ? 'dhe u pagua' : '';
        this.snackBar.open(`Shitja u krijua me sukses ${statusMsg}!`, "Mbyll", { duration: 3000 });
        this.clearSelection();
        this.fetchProducts(); // Refresh product list
        this.loadClient(this.clientId); // Refresh client stats
        this.loadClientSales(this.clientId); // Refresh recent sales
      },
      error: (error) => {
        console.error("Error creating sale:", error);
        const errorMsg = error?.error?.error || "Gabim ne krijimin e shitjes";
        this.snackBar.open(errorMsg, "Mbyll", { duration: 5000 });
      },
    });
  }

  clearSelection(): void {
    this.selectedProduct = null;
    this.saleQuantity = 1;
    this.salePrice = 0;
    this.isPaid = true;
    this.searchText = "";
    this.lastSoldPrice = null;
    this.lastSoldCurrency = null;
    this.paymentMethod = "CASH";
    this.currency = "EUR"; // Reset to EUR (matches product prices)
  }

  // Helpers for recent sales table
  formatSaleDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('sq-AL', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  formatSaleCurrency(amount: number, currency: string): string {
    const symbols: { [key: string]: string } = { 'EUR': '€', 'USD': '$', 'LEK': 'Lek' };
    return `${amount.toFixed(2)} ${symbols[currency] || currency}`;
  }

  getSaleStatusClass(status: string): string {
    const classes: { [key: string]: string } = {
      'COMPLETED': 'status-completed',
      'PARTIAL': 'status-partial',
      'PENDING': 'status-pending'
    };
    return classes[status] || 'status-pending';
  }

  getSaleStatusLabel(status: string): string {
    const labels: { [key: string]: string } = {
      'COMPLETED': 'Paguar',
      'PARTIAL': 'Pjesërisht',
      'PENDING': 'Pa Paguar'
    };
    return labels[status] || status;
  }

  goToSale(saleId: number): void {
    this.router.navigate(['/sale', saleId]);
  }
}

