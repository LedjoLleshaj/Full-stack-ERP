import { Component, OnInit } from "@angular/core";
import { MatSnackBar } from "@angular/material/snack-bar";
import { Router } from "@angular/router";

import { Client } from "src/app/models/client.model";
import { Product } from "src/app/models/product.model";
import { ClientService } from "src/app/shared/services/clients-api/client.service";
import { ProductService } from "src/app/shared/services/product-api/product.service";
import { SalesApiService } from "src/app/shared/services/sales-api/sales-api.service";
import { CurrencyExchangeService } from "src/app/shared/services/currency-exchange/currency-exchange.service";

@Component({
  selector: "app-add-sale-view",
  templateUrl: "./add-sale-view.component.html",
  styleUrls: ["./add-sale-view.component.scss"],
})
export class AddSaleViewComponent implements OnInit {
  // Client selection
  availableClients: Client[] = [];
  selectedClient: Client | null = null;
  clientSearchText = "";

  // Product selection
  availableProducts: Product[] = [];
  selectedProduct: Product | null = null;
  productSearchText = "";

  // Sale details
  saleQuantity: number = 1;
  salePrice: number = 0;
  basePriceEUR: number = 0;
  isPaid: boolean = true;
  currentUserId: number = 1; // TODO: Get from auth service
  lastSoldPrice: number | null = null;
  lastSoldCurrency: string | null = null;

  // Payment options
  paymentMethod: string = "CASH";
  paymentMethods: string[] = ["CASH", "CARD"];
  currency: string = "EUR";
  currencies: string[] = ["EUR", "USD", "LEK"];

  isSubmitting = false;

  constructor(
    private clientService: ClientService,
    private productService: ProductService,
    private saleService: SalesApiService,
    private snackBar: MatSnackBar,
    private currencyExchange: CurrencyExchangeService,
    private router: Router
  ) {}

  ngOnInit() {
    this.fetchClients();
    this.fetchProducts();
  }

  // ========= CLIENT METHODS =========
  fetchClients(): void {
    this.clientService.getClients().subscribe({
      next: (clients) => {
        this.availableClients = clients;
      },
      error: (err) => {
        console.error("Failed to fetch clients:", err);
        this.snackBar.open("Gabim ne ngarkimin e klienteve", "Mbyll", { duration: 3000 });
      },
    });
  }

  filteredClients(): Client[] {
    if (!this.clientSearchText) {
      return this.availableClients;
    }
    const search = this.clientSearchText.toLowerCase();
    return this.availableClients.filter(
      (c) =>
        c.firstname.toLowerCase().includes(search) ||
        c.lastname.toLowerCase().includes(search)
    );
  }

  onClientSelect(event: any): void {
    const client = event.option.value;
    this.selectedClient = client;
    this.clientSearchText = `${client.firstname} ${client.lastname}`;
    
    // Reset last sold price when client changes
    this.lastSoldPrice = null;
    this.lastSoldCurrency = null;
    
    // If product is already selected, fetch last sold price for this client
    if (this.selectedProduct?.id && this.selectedClient?.id) {
      this.fetchLastSoldPrice();
    }
  }

  displayClient(client: Client | null): string {
    return client ? `${client.firstname} ${client.lastname}` : "";
  }

  // ========= PRODUCT METHODS =========
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

  filteredProducts(): Product[] {
    if (!this.productSearchText) {
      return this.availableProducts;
    }
    return this.availableProducts.filter((p) =>
      p.name.toLowerCase().includes(this.productSearchText.toLowerCase())
    );
  }

  onProductSelect(event: any): void {
    const product = event.option.value;
    this.selectedProduct = product;
    if (this.selectedProduct) {
      this.salePrice = this.selectedProduct.price;
      this.basePriceEUR = this.selectedProduct.price;
      this.currency = "EUR";
      this.saleQuantity = 1;
      this.productSearchText = this.selectedProduct.name;

      // Fetch last sold price if client is selected
      if (this.selectedClient?.id) {
        this.fetchLastSoldPrice();
      }
    }
  }

  displayProduct(product: Product | null): string {
    return product ? product.name : "";
  }

  private fetchLastSoldPrice(): void {
    if (!this.selectedClient?.id || !this.selectedProduct?.id) return;
    
    this.saleService.getLastSoldPrice(this.selectedClient.id, this.selectedProduct.id).subscribe({
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

  // ========= SALE METHODS =========
  enforceMax(event: any) {
    const input = event.target as HTMLInputElement;
    const max = this.selectedProduct?.disponibility ?? 0;

    if (+input.value > max) {
      input.value = String(max);
      this.saleQuantity = max;
    }

    if (input.value.length > max.toString().length) {
      input.value = input.value.slice(0, max.toString().length);
    }
  }

  onCurrencyChange(): void {
    if (!this.selectedProduct || this.basePriceEUR === 0) return;

    if (this.currency === "EUR") {
      this.salePrice = this.basePriceEUR;
    } else {
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

  getTotal(): number {
    return this.salePrice * this.saleQuantity;
  }

  canCreateSale(): boolean {
    return (
      this.selectedClient != null &&
      this.selectedProduct != null &&
      this.saleQuantity > 0 &&
      this.saleQuantity <= this.selectedProduct.disponibility &&
      this.salePrice > 0 &&
      !this.isSubmitting
    );
  }

  createSale(): void {
    if (!this.canCreateSale() || !this.selectedProduct || !this.selectedClient) {
      return;
    }

    this.isSubmitting = true;
    const total = this.getTotal();

    const newSale: any = {
      prod: this.selectedProduct.id,
      prod_price: this.salePrice,
      quantity: this.saleQuantity,
      user: this.currentUserId,
      client_id: this.selectedClient.id,
      currency: this.currency,
    };

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
        const statusMsg = response.transaction_status === "COMPLETED" ? "dhe u pagua" : "";
        this.snackBar.open(`Shitja u krijua me sukses ${statusMsg}!`, "Mbyll", { duration: 3000 });
        this.isSubmitting = false;
        this.router.navigate(["/sales"]);
      },
      error: (error) => {
        console.error("Error creating sale:", error);
        const errorMsg = error?.error?.error || "Gabim ne krijimin e shitjes";
        this.snackBar.open(errorMsg, "Mbyll", { duration: 5000 });
        this.isSubmitting = false;
      },
    });
  }

  clearSelection(): void {
    this.selectedClient = null;
    this.clientSearchText = "";
    this.selectedProduct = null;
    this.productSearchText = "";
    this.saleQuantity = 1;
    this.salePrice = 0;
    this.isPaid = true;
    this.lastSoldPrice = null;
    this.lastSoldCurrency = null;
    this.paymentMethod = "CASH";
    this.currency = "EUR";
  }
}
