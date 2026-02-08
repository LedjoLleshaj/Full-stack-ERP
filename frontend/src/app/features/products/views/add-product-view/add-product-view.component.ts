import { Component, OnInit, OnDestroy } from "@angular/core";
import { FormBuilder, FormGroup, Validators, FormControl } from "@angular/forms";
import { ProductService } from "../../../../shared/services/product-api/product.service";
import { Router } from "@angular/router";
import { ProductCategory } from "../../../../models/product-category.model";
import { ProductName } from "../../../../models/product-name.model";
import { InventoryService } from "src/app/shared/services/inventory-api/inventory.service";
import { SupplierService } from "src/app/shared/services/suppliers-api/supplier.service";
import { Supplier } from "../../../../models/supplier.model";
import { Observable, Subject, of } from "rxjs";
import { map, startWith, takeUntil, debounceTime, switchMap, catchError } from "rxjs/operators";

@Component({
  selector: "app-add-product-view",
  templateUrl: "./add-product-view.component.html",
  styleUrls: ["./add-product-view.component.scss"],
})
export class AddProductViewComponent implements OnInit, OnDestroy {
  productForm: FormGroup;
  categories: ProductCategory[] = [];
  names: ProductName[] = [];
  suppliers: Supplier[] = [];

  // Autocomplete
  filteredNames$: Observable<ProductName[]> = of([]);
  filteredCategories$: Observable<ProductCategory[]> = of([]);
  
  // Track if user is creating a new product name (not found in existing list)
  isNewProductName = false;
  
  // Category form control for new products
  categoryControl = new FormControl("");

  private destroy$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private productService: ProductService,
    private inventoryService: InventoryService,
    private supplierService: SupplierService,
    private router: Router
  ) {
    this.productForm = this.fb.group({
      name: ["", Validators.required],
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
    this.setupAutocomplete();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
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

  setupAutocomplete() {
    // Filter product names as user types
    this.filteredNames$ = this.productForm.get("name")!.valueChanges.pipe(
      startWith(""),
      debounceTime(150),
      map((value) => this.filterProductNames(value || ""))
    );

    // Track if the entered name is new (not in the list)
    this.productForm.get("name")!.valueChanges.pipe(
      takeUntil(this.destroy$),
      debounceTime(300)
    ).subscribe((value) => {
      const trimmedValue = (value || "").trim().toLowerCase();
      const existingName = this.names.find(
        (n) => n.product_name.toLowerCase() === trimmedValue
      );
      this.isNewProductName = trimmedValue.length > 0 && !existingName;
    });

    // Filter categories as user types
    this.filteredCategories$ = this.categoryControl.valueChanges.pipe(
      startWith(""),
      debounceTime(150),
      map((value) => this.filterCategories(value || ""))
    );
  }

  filterProductNames(value: string): ProductName[] {
    const filterValue = value.toLowerCase();
    return this.names.filter((name) =>
      name.product_name.toLowerCase().includes(filterValue)
    );
  }

  filterCategories(value: string): ProductCategory[] {
    const filterValue = value.toLowerCase();
    return this.categories.filter((cat) =>
      cat.category_name.toLowerCase().includes(filterValue)
    );
  }

  /**
   * Get category name by ID for display in autocomplete options
   */
  getCategoryName(categoryId: number): string {
    const category = this.categories.find((c) => c.id === categoryId);
    return category ? category.category_name : "";
  }

  onSubmit() {
    if (this.productForm.valid) {
      const productName = this.productForm.get("name")!.value.trim();
      
      // Check if this is an existing product name
      const existingName = this.names.find(
        (n) => n.product_name.toLowerCase() === productName.toLowerCase()
      );

      if (existingName) {
        // Use existing product name - submit directly
        this.submitInventoryUpdate();
      } else {
        // New product name - need to create it first with category
        const categoryName = this.categoryControl.value?.trim();
        
        if (!categoryName) {
          // Show error - category is required for new products
          console.error("Category is required for new products");
          return;
        }

        // Create new product name (and category if needed)
        this.productService.addProductName(productName, categoryName).subscribe({
          next: (response) => {
            console.log("Product name created:", response);
            // Refresh the names list
            this.names.push(response.product_name);
            // If new category was created, add it too
            if (response.created && response.category) {
              const existingCat = this.categories.find(c => c.id === response.category.id);
              if (!existingCat) {
                this.categories.push(response.category);
              }
            }
            // Now submit the inventory update
            this.submitInventoryUpdate();
          },
          error: (error) => {
            console.error("Error creating product name:", error);
          },
        });
      }
    }
  }

  private submitInventoryUpdate() {
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
