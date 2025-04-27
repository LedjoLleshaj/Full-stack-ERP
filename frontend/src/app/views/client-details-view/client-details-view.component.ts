import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { MatDialog } from "@angular/material/dialog";

import { Client } from "src/app/models/client.model";
import { Product } from "src/app/models/product.model";
import { ClientService } from "src/app/shared/services/clients-api/client.service";
import { ProductService } from "src/app/shared/services/product-api/product.service";
import { SalesApiService } from "src/app/shared/services/sales-api/sales-api.service";
import { ConfirmDialogComponent } from "src/app/dialogs/confirm-dialog/confirm-dialog.component";

@Component({
  selector: "app-client-details-view",
  templateUrl: "./client-details-view.component.html",
  styleUrls: ["./client-details-view.component.scss"],
})
export class ClientDetailsViewComponent implements OnInit {
  client!: Client;
  clientId!: number;
  totalBought = 0;
  unpaidBalance = 0;
  searchText = "";
  availableProducts: Product[] = [];
  currentUserId: number = 1; // ⚡ Set this properly, or get it from auth service

  constructor(
    private route: ActivatedRoute,
    private clientService: ClientService,
    private productService: ProductService,
    private saleService: SalesApiService,
    private dialog: MatDialog
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

  confirmPaymentStatus(product: Product): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: "300px",
      data: {
        title: "Pagesa",
        message: "Ka paguar klienti?",
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.addProductToSale(product, true);
      } else {
        this.addProductToSale(product, false);
      }
    });
  }

  addProductToSale(product: Product, isPaid: boolean): void {
    console.log("Adding product to sale:", product, this.client, isPaid);

    const newSale: any = {
      prod: product.id,
      prod_price: product.price,
      quantity: product.selectedQuantity, // Default quantity
      is_paid: isPaid,
      user: this.currentUserId, // Adjust if you get user from AuthService
      client: this.clientId,
    };

    console.log("Temporary Sale:", newSale);

    this.saleService.createSale(newSale).subscribe({
      next: (response) => {
        console.log("Sale created successfully:", response);
        this.fetchProducts(); // Refresh product list after sale
      },
      error: (error) => {
        console.error("Error creating sale:", error);
      },
    });
  }
}
