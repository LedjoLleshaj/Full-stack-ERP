import { Component, OnInit, Output, EventEmitter } from "@angular/core";
import { NgFor } from "@angular/common";
import { MatChipsModule } from "@angular/material/chips";
import { ProductCategory } from "src/app/models/product-category.model";
import { ProductService } from "src/app/shared/services/product-api/product.service";
@Component({
  selector: "app-chips",
  templateUrl: "./chips.component.html",
  standalone: true,
  imports: [MatChipsModule, NgFor],
})
export class ChipsComponent implements OnInit {
  categories: ProductCategory[] = [];
  selected: string[] = [];
  @Output() selectedCategories = new EventEmitter<string[]>();

  constructor(private productService: ProductService) {}

  ngOnInit() {
    this.productService.getProductCategories().subscribe((categories) => {
      this.categories = categories;
    });
  }

  onChipSelectionChange(event: any): void {
    const categoryId = parseInt(event.source.value);
    
    // Find the category object by ID (not by array index!)
    const category = this.categories.find(cat => cat.id === categoryId);
    
    if (!category) {
      console.error('Category not found for ID:', categoryId);
      return;
    }

    if (event.source.selected) {
      if (!this.selected.includes(category.category_name)) {
        this.selected.push(category.category_name);
      }
    } else {
      this.selected = this.selected.filter((catName) => catName !== category.category_name);
    }

    this.selectedCategories.emit(this.selected);
    console.log('Selected categories:', this.selected);
  }
}
