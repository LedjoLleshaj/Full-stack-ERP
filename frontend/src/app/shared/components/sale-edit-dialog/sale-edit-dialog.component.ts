import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { SaleDetails } from '../../../models/sale.model';
import { SaleFormService } from '../../services/sale-form/sale-form.service';

export interface SaleEditDialogData {
  transactionId: number;
  saleDetails: SaleDetails;
}

@Component({
  selector: 'app-sale-edit-dialog',
  templateUrl: './sale-edit-dialog.component.html',
  styleUrls: ['./sale-edit-dialog.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatAutocompleteModule,
    MatIconModule,
    MatSnackBarModule,
  ]
})
export class SaleEditDialogComponent implements OnInit {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: SaleEditDialogData,
    private dialogRef: MatDialogRef<SaleEditDialogComponent>,
    public saleFormService: SaleFormService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.saleFormService.loadTaxRates();
    this.saleFormService.loadProducts();
    this.saleFormService.loadClients();
    this.saleFormService.loadPaymentTerms();
    this.saleFormService.loadForEdit(this.data.saleDetails);
  }

  get state() { return this.saleFormService.state; }

  addItem(): void { this.saleFormService.addItem(); }
  removeItem(i: number): void { this.saleFormService.removeItem(i); }

  onProductSelect(index: number, event: any): void {
    this.saleFormService.onItemProductSelect(index, event.option.value);
  }

  getItemLineTotal(i: number): number {
    return this.saleFormService.getItemLineTotal(i);
  }

  getGrandTotal(): number { return this.saleFormService.getGrandTotal(); }

  onSave(): void {
    if (!this.saleFormService.canCreateSale()) return;
    this.saleFormService.updateSale(this.data.transactionId).subscribe({
      next: (resp) => {
        this.dialogRef.close(resp);
      },
      error: (err) => {
        this.snackBar.open(err?.error?.error || 'Gabim gjatë ruajtjes', 'OK', { duration: 4000 });
      }
    });
  }

  onCancel(): void {
    this.dialogRef.close(null);
  }

  displayProduct(product: any): string {
    return product ? product.name : '';
  }

  filterProducts(index: number, searchText: string): any[] {
    if (!searchText) return this.state.availableProducts;
    const lower = searchText.toLowerCase();
    return this.state.availableProducts.filter(p => p.name.toLowerCase().includes(lower));
  }

  trackByIndex(index: number): number { return index; }
}
