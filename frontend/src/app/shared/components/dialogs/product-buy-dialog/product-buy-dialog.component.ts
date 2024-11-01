import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-product-buy-dialog',
  templateUrl: './product-buy-dialog.component.html',
  styleUrls: ['./product-buy-dialog.component.scss']
})
export class ProductBuyDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<ProductBuyDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  closeDialog(): void {
    this.dialogRef.close();
  }

  addToCart(data: any) {
    console.log('Adding to cart:', data);
    
    const productKey = `product_${data.id}`;
    const existingProduct = localStorage.getItem(productKey);

    if (existingProduct) {
      console.warn('This product is already in the cart:', data.name);
      alert('This product is already in your cart.');
    } else {
      const cartItem = {
        id: data.id,
        name: data.name,
        category: data.category,
        price: data.price,
      };

      const cartItems = JSON.parse(localStorage.getItem('cartItems') || '[]');
      cartItems.push(cartItem);
      localStorage.setItem('cartItems', JSON.stringify(cartItems));
      
      console.log('Product added to cart:', cartItem);
      alert('Product added to cart successfully!');
    }
  }

  buyProduct(data: any) {
    console.log('Buying product:', data);
    alert('Product bought successfully!');
    this.closeDialog();
  }
}
