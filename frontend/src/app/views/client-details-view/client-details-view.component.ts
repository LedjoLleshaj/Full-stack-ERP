import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";

import { Client } from "src/app/models/client.model";
import { Product } from "src/app/models/product.model";
import { ClientService } from "src/app/shared/services/clients-api/client.service";
import { ProductService } from "src/app/shared/services/product-api/product.service";

@Component({
  selector: "app-client-details-view",
  templateUrl: "./client-details-view.component.html",
  styleUrls: ["./client-details-view.component.scss"],
})
export class ClientDetailsViewComponent implements OnInit {
  client!: Client;
  totalBought = 0;
  unpaidBalance = 0;

  searchText = "";
  availableProducts: Product[] = [];

  constructor(
    private route: ActivatedRoute,
    private clientService: ClientService,
    private productService: ProductService
  ) {}

  ngOnInit() {
    const clientId = Number(this.route.snapshot.paramMap.get("id"));
    if (clientId) {
      this.loadClient(clientId);
    }
    this.fetchProducts();
  }

  private loadClient(clientId: number): void {
    this.clientService.getClientById(clientId).subscribe({
      next: (data: Client) => {
        this.client = data;
        // Optionally calculate totals here
      },
      error: (err) => {
        console.error("Failed to load client:", err);
      },
    });
  }

  fetchProducts(): void {
    this.productService.getProducts().subscribe({
      next: (products) => {
        // only keep the products that are not sold out
        this.availableProducts = products.filter((product) => product.disponibility > 0);
      },
      error: (err) => {
        console.error("Failed to fetch products:", err);
      },
    });
  }

  filteredProducts(): Product[] {
    return this.availableProducts.filter((p) => p.name.toLowerCase().includes(this.searchText.toLowerCase()));
  }

  onAddSale(): void {
    console.log("Add Sale for:", this.client?.id);
    // Trigger navigation or modal for adding sale
  }

  selectProduct(product: Product): void {
    // maybe open dialog to confirm quantity and price, then register sale
    console.log("Selected product:", product);
  }

  addProductToSale(product: Product): void {
    // Logic to add product to sale
    console.log("Product added to sale:", product);
  }
}
