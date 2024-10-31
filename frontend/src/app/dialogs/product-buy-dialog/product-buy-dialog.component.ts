import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-product-buy-dialog',
  templateUrl: './product-buy-dialog.component.html',
  styleUrls: ['./product-buy-dialog.component.scss']
})
export class ProductBuyDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<ProductBuyDialogComponent>, // Inject MatDialogRef
    @Inject(MAT_DIALOG_DATA) public data: any // Inject the data passed to the dialog
  ) {}

  // Method to close the dialog
  closeDialog(): void {
    this.dialogRef.close();
  }

  // You can also implement addToCart and buyProduct methods here
  addToCart(data: any) {
    console.log('Adding to cart:', data);
    // Logic to add the product to the cart
  }

  buyProduct(data: any) {
    console.log('Buying product:', data);
    // Logic to handle the product purchase
  }
}
