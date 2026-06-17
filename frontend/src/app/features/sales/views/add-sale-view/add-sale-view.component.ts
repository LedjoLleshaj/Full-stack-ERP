import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { Subscription } from 'rxjs';

import { SaleFormService } from 'src/app/shared/services/sale-form/sale-form.service';
import { Client } from '../../../../models/client.model';
import { Product } from '../../../../models/product.model';

@Component({
  selector: 'app-add-sale-view',
  templateUrl: './add-sale-view.component.html',
  styleUrls: ['./add-sale-view.component.scss'],
})
export class AddSaleViewComponent implements OnInit, OnDestroy {
  private stateChangeSub?: Subscription;

  constructor(
    public saleFormService: SaleFormService,
    private router: Router,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.saleFormService.resetForm();
    this.saleFormService.loadClients();
    this.saleFormService.loadProducts();
    this.saleFormService.loadTaxRates();
    this.saleFormService.loadPaymentTerms();

    // Subscribe to state changes for change detection
    this.stateChangeSub = this.saleFormService.onStateChange.subscribe(() => {
      // trigger Angular change detection
    });

    // Check for edit mode via route param :transactionId (wired in Task 10)
    const transactionId = this.route.snapshot.paramMap.get('transactionId');
    if (transactionId) {
      this.loadForEdit(parseInt(transactionId, 10));
    }
  }

  ngOnDestroy(): void {
    this.stateChangeSub?.unsubscribe();
  }

  get state() {
    return this.saleFormService.state;
  }

  // ======== Item management ========

  addItem(): void {
    this.saleFormService.addItem();
  }

  removeItem(index: number): void {
    this.saleFormService.removeItem(index);
  }

  // ======== Autocomplete handlers ========

  onProductSelect(index: number, event: MatAutocompleteSelectedEvent): void {
    this.saleFormService.onItemProductSelect(index, event.option.value as Product);
  }

  onClientSelect(event: MatAutocompleteSelectedEvent): void {
    this.saleFormService.onClientSelect(event.option.value as Client);
  }

  onCurrencyChange(currency: string): void {
    this.saleFormService.onCurrencyChange(currency);
  }

  // ======== Display helpers ========

  displayProduct(product: Product | null): string {
    return product ? product.name : '';
  }

  displayClient(client: Client | null): string {
    return client ? `${client.firstname} ${client.lastname}` : '';
  }

  // ======== Filtered lists ========

  filteredClients(): Client[] {
    return this.saleFormService.filteredClients();
  }

  filteredProductsForItem(index: number): Product[] {
    return this.saleFormService.filteredProductsForItem(index);
  }

  // ======== Calculations ========

  getItemLineTotal(index: number): number {
    return this.saleFormService.getItemLineTotal(index);
  }

  getGrandSubtotal(): number {
    return this.saleFormService.getGrandSubtotal();
  }

  getGrandDiscount(): number {
    return this.saleFormService.getGrandDiscount();
  }

  getGrandTax(): number {
    return this.saleFormService.getGrandTax();
  }

  getGrandTotal(): number {
    return this.saleFormService.getGrandTotal();
  }

  // ======== Submission ========

  createSale(): void {
    if (!this.saleFormService.canCreateSale()) return;
    this.state.isSubmitting = true;
    this.saleFormService.createSale().subscribe({
      next: (resp) => {
        this.state.isSubmitting = false;
        this.snackBar.open('Shitja u krijua me sukses!', 'OK', { duration: 3000 });
        this.router.navigate(['/sales', resp.transaction_id]);
      },
      error: (err) => {
        this.state.isSubmitting = false;
        this.snackBar.open(
          err?.error?.error || 'Gabim gjatë krijimit të shitjes',
          'OK',
          { duration: 4000 }
        );
      },
    });
  }

  // ======== Edit mode (wired in Task 10) ========

  private loadForEdit(_transactionId: number): void {
    // Will be connected in Task 10 when the details view is done
  }

  // ======== Track by ========

  trackByIndex(index: number): number {
    return index;
  }
}
