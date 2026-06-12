import { Component, OnInit } from "@angular/core";
import { InventoryService } from "src/app/shared/services/inventory-api/inventory.service";
import { ClientService } from "src/app/shared/services/clients-api/client.service";
import { LowStockProduct } from "../../../../models/low-stock.model";
import { Client } from "../../../../models/client.model";

@Component({
  selector: "app-alerts-view",
  templateUrl: "./alerts-view.component.html",
})
export class AlertsViewComponent implements OnInit {
  lowStockProducts: LowStockProduct[] = [];
  clientsWithDebt: Client[] = [];

  stockColumns: string[] = ['name', 'category', 'quantity', 'reorder_level', 'reorder_quantity', 'price'];
  debtColumns: string[] = ['name', 'city', 'phone', 'unpaidBalance'];

  constructor(
    private inventoryService: InventoryService,
    private clientService: ClientService
  ) {}

  ngOnInit() {
    this.loadLowStockProducts();
    this.loadClientsWithDebt();
  }

  loadLowStockProducts() {
    this.inventoryService.getLowStock().subscribe((products) => {
      this.lowStockProducts = products;
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
