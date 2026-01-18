import { Component, OnInit } from "@angular/core";
import { FormBuilder, FormGroup, Validators } from "@angular/forms";
import { ProductService } from "../../../../shared/services/product-api/product.service";
import { Router } from "@angular/router";
import { ProductCategory } from "../../../../models/product-category.model";
import { ProductName } from "../../../../models/product-name.model";
import { InventoryService } from "src/app/shared/services/inventory-api/inventory.service";
import { SupplierService } from "src/app/shared/services/suppliers-api/supplier.service";
import { Supplier } from "../../../../models/supplier.model";

@Component({
  selector: "app-add-product-view",
  templateUrl: "./add-product-view.component.html",
  styleUrls: ["./add-product-view.component.scss"],
})
export class AddProductViewComponent implements OnInit {
  productForm: FormGroup;
  categories: ProductCategory[] = [];
  names: ProductName[] = [];
  suppliers: Supplier[] = [];

  constructor(
    private fb: FormBuilder,
    private productService: ProductService,
    private inventoryService: InventoryService,
    private supplierService: SupplierService,
    private router: Router
  ) {
    this.productForm = this.fb.group({
      name: ["", Validators.required],
      //category: ["", Validators.required],
      price: [0, [Validators.min(0)]],
      quantity: [0, [Validators.required, Validators.min(1)]],
      supplier_id: [null, Validators.required],
      description: [""],
      is_paid: [true],
    });
  }

  ngOnInit(): void {
    this.fetchCategories();
    this.fetchProductNames();
    this.fetchSuppliers();
  }

  fetchCategories() {
    this.productService.getProductCategories().subscribe({
      next: (data: ProductCategory[]) => {
        this.categories = data;
      },
      error: (error) => {
        console.error("Error fetching categories:", error);
      },
    });
  }

  fetchProductNames() {
    this.productService.getProductNames().subscribe({
      next: (data: ProductName[]) => {
        this.names = data;
      },
      error: (error) => {
        console.error("Error fetching product names:", error);
      },
    });
  }

  fetchSuppliers() {
    this.supplierService.getSuppliers().subscribe({
      next: (data: Supplier[]) => {
        this.suppliers = data;
      },
      error: (error) => {
        console.error("Error fetching suppliers:", error);
      },
    });
  }

  onSubmit() {
    if (this.productForm.valid) {
      this.inventoryService.updateInventory(this.productForm.value).subscribe({
        next: (product) => {
          console.log("Product added:", product);
          this.router.navigate(["/products"]);
        },
        error: (error) => {
          console.error("Error adding product:", error);
        },
      });
    }
  }
}
