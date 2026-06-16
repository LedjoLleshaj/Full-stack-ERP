import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable, map, startWith, pairwise } from 'rxjs'; // Added pairwise
import { MatSnackBar } from '@angular/material/snack-bar'; // Added

import { SaleResponse } from '../../../models/sale.model';
import { Product } from '../../../models/product.model';
import { TaxRate } from '../../../models/tax-rate.model';
import { ProductService } from '../../services/product-api/product.service';
import { CurrencyExchangeService } from '../../services/currency-exchange/currency-exchange.service'; // Added
import { TaxRateApiService } from '../../services/tax-rate-api/tax-rate-api.service';

export interface SaleEditDialogData {
  sale: SaleResponse;
  products: Product[];
  totalPaid?: number;
  taxRateId?: number;
  discountType?: string | null;
  discountValue?: number;
}

@Component({
  selector: 'app-sale-edit-dialog',
  templateUrl: './sale-edit-dialog.component.html',
  styleUrls: ['./sale-edit-dialog.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatAutocompleteModule,
    MatIconModule,
    MatProgressSpinnerModule
  ]
})
export class SaleEditDialogComponent implements OnInit {
  editForm!: FormGroup;
  filteredProducts!: Observable<Product[]>;
  isSaving = false;
  currencies = ['EUR', 'USD', 'LEK'];
  hasPayments = false;
  totalPaid = 0;
  isLoadingRate = false; // Added to track rate fetching
  readonly ROUNDING_TOLERANCE = 0.10;
  taxRates: TaxRate[] = [];
  selectedTaxRateId: number | null = null;
  discountType: string | null = null;
  discountValue: number = 0;

  constructor(
    private fb: FormBuilder,
    private productService: ProductService,
    private currencyService: CurrencyExchangeService, // Added
    private taxRateService: TaxRateApiService,
    private snackBar: MatSnackBar, // Added for error reporting
    public dialogRef: MatDialogRef<SaleEditDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: SaleEditDialogData
  ) {}

  ngOnInit(): void {
    // Check if sale has payments
    this.totalPaid = this.data.totalPaid || 0;
    this.hasPayments = this.totalPaid > 0;

    // Load tax rates and discount
    this.selectedTaxRateId = this.data.taxRateId || null;
    this.discountType = this.data.discountType || null;
    this.discountValue = this.data.discountValue || 0;
    this.taxRateService.getTaxRates().subscribe(rates => {
      this.taxRates = rates;
    });
    
    // Initialize form with current sale data
    this.editForm = this.fb.group({
      product: [this.data.sale.product, Validators.required],
      quantity: [this.data.sale.quantity, [Validators.required, Validators.min(0.01)]],
      prod_price: [this.data.sale.prod_price, [Validators.required, Validators.min(0)]],
      currency: [this.data.sale.currency || 'EUR', Validators.required]
    });

    // Setup product autocomplete filter
    this.filteredProducts = this.editForm.get('product')!.valueChanges.pipe(
      startWith(this.data.sale.product),
      map(value => {
        const filterValue = typeof value === 'string' ? value : value?.name || '';
        return this._filterProducts(filterValue);
      })
    );

    // Auto-calculate total when quantity or price changes
    this.editForm.get('quantity')?.valueChanges.subscribe(() => this.calculateTotal());
    this.editForm.get('prod_price')?.valueChanges.subscribe(() => this.calculateTotal());

    // Listen for currency changes to auto-convert price
    this.editForm.get('currency')?.valueChanges.pipe(
      startWith(this.editForm.get('currency')?.value),
      pairwise()
    ).subscribe(([prevCurrency, nextCurrency]) => {
      if (prevCurrency && nextCurrency && prevCurrency !== nextCurrency) {
        this.convertPrice(prevCurrency, nextCurrency);
      }
    });
  }

  private _filterProducts(value: string): Product[] {
    const filterValue = value.toLowerCase();
    return this.data.products.filter(product => 
      product.name.toLowerCase().includes(filterValue)
    );
  }

  displayProduct(product: Product | null): string {
    return product ? product.name : '';
  }

  calculateTotal(): number {
    const quantity = this.editForm.get('quantity')?.value || 0;
    const price = this.editForm.get('prod_price')?.value || 0;
    return quantity * price;
  }

  getDiscountAmount(): number {
    if (!this.discountType || this.discountValue <= 0) return 0;
    const subtotal = this.calculateTotal();
    if (this.discountType === 'PERCENT') {
      return Math.round(subtotal * this.discountValue / 100 * 100) / 100;
    }
    return Math.min(this.discountValue, subtotal);
  }

  getDiscountedSubtotal(): number {
    return this.calculateTotal() - this.getDiscountAmount();
  }

  getTaxAmount(): number {
    if (!this.selectedTaxRateId) return 0;
    const rate = this.taxRates.find(r => r.id === this.selectedTaxRateId);
    if (!rate) return 0;
    return Math.round(this.getDiscountedSubtotal() * parseFloat(rate.rate) / 100 * 100) / 100;
  }

  getTotalWithTax(): number {
    return this.getDiscountedSubtotal() + this.getTaxAmount();
  }

  /**
   * Converts the product price when currency changes
   */
  private convertPrice(fromCurrency: string, toCurrency: string): void {
    const currentPrice = this.editForm.get('prod_price')?.value;
    if (!currentPrice || currentPrice <= 0) return;

    this.isLoadingRate = true;
    this.editForm.disable({ emitEvent: false }); // Disable form during fetch

    this.currencyService.getExchangeRate(fromCurrency, toCurrency).subscribe({
      next: (rate) => {
        const newPrice = Math.round(currentPrice * rate * 100) / 100;
        
        // Also convert totalPaid threshold if it exists
        if (this.totalPaid > 0) {
          this.totalPaid = Math.round(this.totalPaid * rate * 100) / 100;
        }

        this.editForm.enable({ emitEvent: false });
        this.editForm.patchValue({ prod_price: newPrice }); // Will trigger total recalc
        this.isLoadingRate = false;
        
        this.snackBar.open(
          `Çmimi u konvertua nga ${fromCurrency} në ${toCurrency} (Kursi: ${rate})`, 
          'OK', 
          { duration: 3000 }
        );
      },
      error: (err) => {
        console.error('Error fetching exchange rate:', err);
        this.editForm.enable({ emitEvent: false });
        this.isLoadingRate = false;
        this.snackBar.open('Gabim në konvertimin e çmimit', 'OK', { duration: 3000 });
      }
    });
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  isTotalInvalid(): boolean {
    if (!this.hasPayments) return false;
    const total = this.getTotalWithTax();
    return total < (this.totalPaid - this.ROUNDING_TOLERANCE);
  }

  onSave(): void {
    if (this.editForm.valid && !this.isTotalInvalid()) {
      this.isSaving = true;
      const formValue = this.editForm.value;

      const updateData: any = {
        prod: formValue.product.id,
        quantity: formValue.quantity,
        prod_price: formValue.prod_price,
        currency: formValue.currency,
        user: this.data.sale.user
      };

      if (this.selectedTaxRateId) {
        updateData.tax_rate_id = this.selectedTaxRateId;
      }

      updateData.discount_type = this.discountType;
      updateData.discount_value = this.discountType ? this.discountValue : 0;

      this.dialogRef.close(updateData);
    }
  }
}
