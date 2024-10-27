import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ProductService } from '../shared/services/product-api/product.service';
import { Router } from '@angular/router';
import { ProductCategory } from '../models/product-category.model';
import { ProductName } from '../models/product-name.model';

@Component({
  selector: 'app-add-product-view',
  templateUrl: './add-product-view.component.html',
  styleUrls: ['./add-product-view.component.scss']
})
export class AddProductViewComponent implements OnInit {
  productForm: FormGroup;
  categories: ProductCategory[] = [];
  names: ProductName[] = [];

  constructor(
    private fb: FormBuilder,
    private productService: ProductService,
    private router: Router
  ) {
    this.productForm = this.fb.group({
      name: ['', Validators.required],
      category: ['', Validators.required],
      price: [0, [Validators.required, Validators.min(0)]],
      description: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    this.fetchCategories();
    this.fetchProductNames();
  }

  fetchCategories() {
    this.productService.getProductCategories().subscribe({
      next: (data: ProductCategory[]) => {
        this.categories = data;
      },
      error: (error) => {
        console.error('Error fetching categories:', error);
      }
    });
  }

  fetchProductNames() {
    this.productService.getProductNames().subscribe({
      next: (data: ProductName[]) => {
        this.names = data;
      },
      error: (error) => {
        console.error('Error fetching product names:', error);
      }
    });
  }

  onSubmit() {
    if (this.productForm.valid) {
      this.productService.addProduct(this.productForm.value).subscribe({
        next: (product) => {
          console.log('Product added:', product);
          this.router.navigate(['/products']);
        },
        error: (error) => {
          console.error('Error adding product:', error);
        }
      });
    }
  }
}
