import { Component, OnInit } from "@angular/core";
import { ProductService } from "src/app/shared/services/product-api/product.service";
import { ClientService } from "src/app/shared/services/clients-api/client.service";
import { Product } from "src/app/models/product.model";
import { Client } from "src/app/models/client.model";

@Component({
  selector: "app-alerts-view",
  templateUrl: "./alerts-view.component.html",
})
export class AlertsViewComponent implements OnInit {
  lowStockProducts: Product[] = [];
  clientsWithDebt: Client[] = [];
  
  lowStockThreshold = 5; // Products with stock under 5 units are considered low

  stockColumns: string[] = ['name', 'category', 'disponibility', 'price'];
  debtColumns: string[] = ['name', 'city', 'phone', 'unpaidBalance'];

  constructor(
    private productService: ProductService,
    private clientService: ClientService
  ) {}

  ngOnInit() {
    this.loadLowStockProducts();
    this.loadClientsWithDebt();
  }

  loadLowStockProducts() {
    this.productService.getProducts().subscribe((products) => {
      this.lowStockProducts = products.filter(
        (p) => p.disponibility < this.lowStockThreshold
      ).sort((a, b) => a.disponibility - b.disponibility);
    });
  }

  loadClientsWithDebt() {
    this.clientService.getClients().subscribe((clients) => {
      this.clientsWithDebt = clients.filter(
        (c) => c.unpaidBalance > 0
      ).sort((a, b) => b.unpaidBalance - a.unpaidBalance);
    });
  }
}
