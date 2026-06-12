import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ReturnRequest } from 'src/app/models/sale.model';

export interface ReturnDialogData {
  saleId: number;
  items: {
    sale_line_id: number;
    product_name: string;
    original_quantity: number;
    already_returned: number;
    unit_price: number;
    currency: string;
  }[];
  transactionCurrency: string;
  totalPaid: number;
  totalAmount: number;
}

interface ReturnLineItem {
  sale_line_id: number;
  product_name: string;
  original_quantity: number;
  already_returned: number;
  max_returnable: number;
  unit_price: number;
  return_quantity: number;
}

@Component({
  selector: 'app-return-dialog',
  templateUrl: './return-dialog.component.html',
  styleUrls: ['./return-dialog.component.scss'],
})
export class ReturnDialogComponent implements OnInit {
  lineItems: ReturnLineItem[] = [];
  refundMethod: string = 'CASH';
  refundMethods: string[] = ['CASH', 'CARD'];
  refundCurrency: string = 'EUR';
  currencies: string[] = ['LEK', 'EUR', 'USD'];
  notes: string = '';

  constructor(
    public dialogRef: MatDialogRef<ReturnDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ReturnDialogData
  ) {}

  ngOnInit(): void {
    this.refundCurrency = this.data.transactionCurrency;
    this.lineItems = this.data.items.map(item => ({
      sale_line_id: item.sale_line_id,
      product_name: item.product_name,
      original_quantity: item.original_quantity,
      already_returned: item.already_returned,
      max_returnable: item.original_quantity - item.already_returned,
      unit_price: item.unit_price,
      return_quantity: 0,
    }));
  }

  get returnValue(): number {
    return this.lineItems.reduce(
      (sum, item) => sum + item.return_quantity * item.unit_price,
      0
    );
  }

  get estimatedRefund(): number {
    const newTotal = this.data.totalAmount - this.returnValue;
    return Math.max(0, this.data.totalPaid - newTotal);
  }

  get hasReturnItems(): boolean {
    return this.lineItems.some(item => item.return_quantity > 0);
  }

  getMethodLabel(method: string): string {
    return method === 'CASH' ? 'Cash' : 'Kartë';
  }

  onCancel(): void {
    this.dialogRef.close(null);
  }

  onSubmit(): void {
    const items = this.lineItems
      .filter(item => item.return_quantity > 0)
      .map(item => ({
        sale_line_id: item.sale_line_id,
        quantity: item.return_quantity,
      }));

    const request: ReturnRequest = {
      items,
      refund_method: this.refundMethod as 'CASH' | 'CARD',
      refund_currency: this.refundCurrency,
      notes: this.notes || undefined,
    };

    this.dialogRef.close(request);
  }
}
