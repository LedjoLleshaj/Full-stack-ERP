import { Component, OnInit, OnDestroy } from "@angular/core";
import { Subscription } from "rxjs";

import { Client } from "../../../../models/client.model";
import { Product } from "../../../../models/product.model";
import { SaleFormService, SaleFormState } from "src/app/shared/services/sale-form/sale-form.service";

@Component({
  selector: "app-add-sale-view",
  templateUrl: "./add-sale-view.component.html",
  styleUrls: ["./add-sale-view.component.scss"],
})
export class AddSaleViewComponent implements OnInit, OnDestroy {
  // Form state managed by service
  state: SaleFormState;

  // Expose service constants to template
  get paymentMethods(): string[] { return this.saleFormService.paymentMethods; }
  get currencies(): string[] { return this.saleFormService.currencies; }

  private stateChangeSub?: Subscription;

  constructor(private saleFormService: SaleFormService) {
    this.state = this.saleFormService.getInitialState();
  }

  ngOnInit() {
    // Subscribe to state changes for change detection
    this.stateChangeSub = this.saleFormService.onStateChange.subscribe(() => {
      // Trigger change detection if needed
    });

    this.saleFormService.loadClients(this.state);
    this.saleFormService.loadProducts(this.state);
  }

  ngOnDestroy() {
    this.stateChangeSub?.unsubscribe();
  }

  // ========= CLIENT METHODS =========
  filteredClients(): Client[] {
    return this.saleFormService.filteredClients(this.state);
  }

  onClientSelect(event: any): void {
    const client = event.option.value;
    this.saleFormService.onClientSelect(this.state, client);
  }

  displayClient(client: Client | null): string {
    return this.saleFormService.displayClient(client);
  }

  // ========= PRODUCT METHODS =========
  filteredProducts(): Product[] {
    return this.saleFormService.filteredProducts(this.state);
  }

  onProductSelect(event: any): void {
    const product = event.option.value;
    this.saleFormService.onProductSelect(this.state, product);
  }

  displayProduct(product: Product | null): string {
    return this.saleFormService.displayProduct(product);
  }

  // ========= SALE METHODS =========
  enforceMax(event: any): void {
    const input = event.target as HTMLInputElement;
    const value = this.saleFormService.enforceMaxQuantity(this.state, input.value);
    input.value = String(value);
  }

  onCurrencyChange(): void {
    this.saleFormService.onCurrencyChange(this.state);
  }

  getTotal(): number {
    return this.saleFormService.getTotal(this.state);
  }

  canCreateSale(): boolean {
    return this.saleFormService.canCreateSale(this.state);
  }

  createSale(): void {
    this.saleFormService.createSale(this.state, undefined, true).subscribe();
  }

  clearSelection(): void {
    this.saleFormService.clearSelection(this.state);
  }
}
