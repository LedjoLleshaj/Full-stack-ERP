import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommonModule } from '@angular/common';
import { startWith, pairwise } from 'rxjs'; // Added rxjs operators
import { MatSnackBar } from '@angular/material/snack-bar'; // Added snackbar

import { RestockResponse } from '../../../models/restock.model';
import { Product } from '../../../models/product.model';
import { CurrencyExchangeService } from '../../services/currency-exchange/currency-exchange.service'; // Added service

export interface RestockEditDialogData {
  restock: RestockResponse;
  products: Product[];
}

@Component({
  selector: 'app-restock-edit-dialog',
  templateUrl: './restock-edit-dialog.component.html',
  styleUrls: ['./restock-edit-dialog.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatIconModule,
    MatProgressSpinnerModule
  ]
})
export class RestockEditDialogComponent implements OnInit {
  editForm!: FormGroup;
  isSaving = false;
  currencies = ['EUR', 'USD', 'LEK'];
  hasPayments = false;
  isLoadingRate = false; // Added loading state
  totalPaid = 0;
  readonly ROUNDING_TOLERANCE = 0.10;

  constructor(
    private fb: FormBuilder,
    private currencyService: CurrencyExchangeService, // Added service
    private snackBar: MatSnackBar, // Added snackbar
    public dialogRef: MatDialogRef<RestockEditDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: RestockEditDialogData
  ) {}

  ngOnInit(): void {
    // Check if restock has payments
    this.hasPayments = this.data.restock.transaction_info?.status !== 'PENDING';
    
    // Calculate initial values
    // Use transaction total amount if available, otherwise fallback to restock_price
    const totalAmount = this.data.restock.transaction_info?.total_amount 
      ? parseFloat(this.data.restock.transaction_info.total_amount.toString()) 
      : parseFloat(this.data.restock.restock_price);
      
    const quantity = this.data.restock.quantity;
    const unitPrice = quantity > 0 ? totalAmount / quantity : 0;
    
    // Calculate total paid
    this.totalPaid = this.data.restock.payments?.reduce((sum, p) => sum + parseFloat(p.amount), 0) || 0;

    // Initialize form with current restock data
    this.editForm = this.fb.group({
      prod: [this.data.restock.prod, Validators.required],
      quantity: [quantity, [Validators.required, Validators.min(0.01)]],
      // Unit price is editable
      unit_price: [parseFloat(unitPrice.toFixed(2)), [Validators.required, Validators.min(0)]],
      restock_price: [totalAmount, [Validators.required, Validators.min(this.totalPaid - this.ROUNDING_TOLERANCE)]],
      currency: [this.data.restock.transaction_info?.currency || 'EUR', Validators.required]
    });

    // Subscribe to changes to sync values
    this.setupValueSync();

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

  setupValueSync(): void {
    const quantityControl = this.editForm.get('quantity');
    const unitPriceControl = this.editForm.get('unit_price');
    const totalPriceControl = this.editForm.get('restock_price');

    if (!quantityControl || !unitPriceControl || !totalPriceControl) return;

    // When Quantity changes -> Update Total (Unit Price stays same)
    quantityControl.valueChanges.subscribe(qty => {
      if (qty && unitPriceControl.value != null) {
        const newTotal = parseFloat((qty * unitPriceControl.value).toFixed(2));
        totalPriceControl.setValue(newTotal, { emitEvent: false });
      }
    });

    // When Unit Price changes -> Update Total
    unitPriceControl.valueChanges.subscribe(unitPrice => {
      if (unitPrice != null && quantityControl.value) {
        const newTotal = parseFloat((quantityControl.value * unitPrice).toFixed(2));
        totalPriceControl.setValue(newTotal, { emitEvent: false });
      }
    });

    // When Total Price changes -> Update Unit Price
    totalPriceControl.valueChanges.subscribe(totalPrice => {
      if (totalPrice != null && quantityControl.value && quantityControl.value > 0) {
        const newUnit = parseFloat((totalPrice / quantityControl.value).toFixed(2));
        // We update unit price but don't emit event to avoid circular loop
        // However, if we round, it might drift. Let's keep it simple.
        unitPriceControl.setValue(newUnit, { emitEvent: false });
      }
    });
  }

  /**
   * Converts the restock price when currency changes
   */
  private convertPrice(fromCurrency: string, toCurrency: string): void {
    const currentPrice = this.editForm.get('restock_price')?.value;
    if (!currentPrice || currentPrice <= 0) return;

    this.isLoadingRate = true;
    this.editForm.disable({ emitEvent: false }); // Disable form during fetch

    this.currencyService.getExchangeRate(fromCurrency, toCurrency).subscribe({
      next: (rate) => {
        const newTotal = Math.round(currentPrice * rate * 100) / 100;
        
        // Also convert totalPaid threshold to prevent blocking "change back" (e.g. LEK -> EUR)
        // Match backend tolerance if possible, but at least convert the threshold
        if (this.totalPaid > 0) {
          this.totalPaid = Math.round(this.totalPaid * rate * 100) / 100;
        }

        this.editForm.enable({ emitEvent: false });
        
        // Update Total and refresh validator with new totalPaid threshold
        const priceControl = this.editForm.get('restock_price');
        priceControl?.setValidators([
          Validators.required, 
          Validators.min(this.totalPaid - this.ROUNDING_TOLERANCE)
        ]);
        this.editForm.patchValue({ restock_price: newTotal }, { emitEvent: true }); 
        priceControl?.updateValueAndValidity();
        
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

  onSave(): void {
    if (this.editForm.valid) {
      this.isSaving = true;
      this.dialogRef.close(this.editForm.value);
    }
  }

  getProductName(prodId: number): string {
    const product = this.data.products.find(p => p.id === prodId);
    return product ? product.name : '';
  }
}
