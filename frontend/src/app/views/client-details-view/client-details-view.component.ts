import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";

import { Client } from "src/app/models/client.model";
import { Product } from "src/app/models/product.model";
import { ClientService } from "src/app/shared/services/clients-api/client.service";
import { ProductService } from "src/app/shared/services/product-api/product.service";
import { SalesApiService } from "src/app/shared/services/sales-api/sales-api.service";

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
  isPaid: boolean = true;
  currentUserId: number = 1; // ⚡ TODO: Get from auth service

  constructor(
    private route: ActivatedRoute,
    private clientService: ClientService,
    private productService: ProductService,
    private saleService: SalesApiService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.clientId = Number(this.route.snapshot.paramMap.get("id"));
    if (this.clientId) {
      this.loadClient(this.clientId);
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
    if (!this.searchText) {
      return this.availableProducts;
    }
    return this.availableProducts.filter((p) =>
      p.name.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }

  onProductSelect(): void {
    if (this.selectedProduct) {
      this.salePrice = this.selectedProduct.price;
      this.saleQuantity = 1;
    }
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

    const newSale: any = {
      prod: this.selectedProduct.id,
      prod_price: this.salePrice,
      quantity: this.saleQuantity,
      is_paid: this.isPaid,
      user: this.currentUserId,
      client: this.clientId,
    };

    this.saleService.createSale(newSale).subscribe({
      next: (response) => {
        console.log("Sale created successfully:", response);
        this.snackBar.open("Shitja u krijua me sukses!", "Mbyll", { duration: 3000 });
        this.clearSelection();
        this.fetchProducts(); // Refresh product list
        this.loadClient(this.clientId); // Refresh client stats
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
  }
}
