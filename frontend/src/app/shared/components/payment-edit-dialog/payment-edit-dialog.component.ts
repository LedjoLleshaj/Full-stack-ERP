import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import { CurrencyExchangeService } from '../../services/currency-exchange/currency-exchange.service';

@Component({
  selector: 'app-payment-edit-dialog',
  templateUrl: './payment-edit-dialog.component.html',
  styleUrls: ['./payment-edit-dialog.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    MatIconModule
  ]
})
export class PaymentEditDialogComponent implements OnInit {
  paymentForm: FormGroup;
  maxAmount: number = 0;
  currencies = ['EUR', 'USD', 'LEK'];
  paymentMethods = ['CASH', 'CARD'];
  isLoadingRate = false;
  exchangeRateToTrans = 1; // Rate from Transaction -> Selected Currency (for max validation)
  previousCurrency: string;

  constructor(
    private fb: FormBuilder,
    private currencyService: CurrencyExchangeService,
    private dialogRef: MatDialogRef<PaymentEditDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { 
      payment: any, 
      transactionTotal: number, 
      otherPaymentsTotal: number,
      currency: string
    }
  ) {
    // Determine initial amount and currency
    const initialAmount = data.payment.original_amount || data.payment.amount;
    const initialCurrency = data.payment.original_currency || data.payment.currency || data.currency;
    this.previousCurrency = initialCurrency;

    // Initialize exchange rate relative to transaction for validation
    if (this.data.payment.exchange_rate && this.data.payment.exchange_rate > 0) {
      this.exchangeRateToTrans = 1 / this.data.payment.exchange_rate;
    } else {
      this.exchangeRateToTrans = 1;
    }

    this.paymentForm = this.fb.group({
      amount: [initialAmount, [Validators.required, Validators.min(0.01)]],
      currency: [initialCurrency, Validators.required],
      payment_method: [data.payment.payment_method || 'CASH', Validators.required],
      notes: [data.payment.notes || '']
    });
  }

  ngOnInit(): void {
    // Just initialize max amount and validation on load
    this.updateMaxAmount();
  }

  onCurrencyChange(): void {
    const selectedCurrency = this.paymentForm.get('currency')?.value;
    const currentAmount = this.paymentForm.get('amount')?.value || 0;

    // Guard: Only convert if the currency has actually changed
    if (selectedCurrency === this.previousCurrency) {
      return;
    }

    this.isLoadingRate = true;
    
    // 1. Get direct rate from Previous -> Selected for amount conversion
    this.currencyService.getExchangeRate(this.previousCurrency, selectedCurrency).subscribe({
      next: (directRate) => {
        // 2. Also get rate from Transaction -> Selected for max validation
        this.currencyService.getExchangeRate(this.data.currency, selectedCurrency).subscribe({
          next: (transRate) => {
            this.exchangeRateToTrans = transRate;
            this.updateFormAfterRateChange(currentAmount, directRate, selectedCurrency);
            this.isLoadingRate = false;
          },
          error: () => {
            this.isLoadingRate = false;
            // Fallback for transRate but still apply direct conversion if possible
            this.exchangeRateToTrans = 1; 
            this.updateFormAfterRateChange(currentAmount, directRate, selectedCurrency);
          }
        });
      },
      error: () => {
        this.isLoadingRate = false;
      }
    });
  }

  private updateFormAfterRateChange(currentAmount: number, directRate: number, newCurrency: string): void {
    // Convert current amount directly using the fetched rate
    if (directRate > 0 && currentAmount > 0) {
      const newAmount = Math.round(currentAmount * directRate * 100) / 100;
      this.paymentForm.patchValue({ amount: newAmount }, { emitEvent: false });
    }
    
    this.previousCurrency = newCurrency;
    this.updateMaxAmount(); // Update range validation with new exchangeRateToTrans
  }

  private updateMaxAmount(): void {
    const remainingInTransCurr = this.data.transactionTotal - this.data.otherPaymentsTotal;
    // max in selected curr = remaining * (Trans->Selected rate)
    this.maxAmount = Math.round(remainingInTransCurr * this.exchangeRateToTrans * 100) / 100;
    
    const amountControl = this.paymentForm.get('amount');
    amountControl?.setValidators([
      Validators.required, 
      Validators.min(0.01), 
      Validators.max(this.maxAmount + 0.10) // Small tolerance
    ]);
    amountControl?.updateValueAndValidity();
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onSave(): void {
    if (this.paymentForm.valid) {
      this.dialogRef.close(this.paymentForm.value);
    }
  }

  formatCurrency(amount: number, currency?: string): string {
    const curr = currency || this.paymentForm.get('currency')?.value;
    const symbols: { [key: string]: string } = { 'EUR': '€', 'USD': '$', 'LEK': 'Lek' };
    return `${amount.toFixed(2)} ${symbols[curr] || curr}`;
  }
}
