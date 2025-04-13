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
    const cat = parseInt(event.source.value);

    if (event.source.selected) {
      if (!this.selected.includes(this.categories[cat - 1].category_name)) {
        this.selected.push(this.categories[cat - 1].category_name);
      }
    } else {
      this.selected = this.selected.filter((category) => category !== this.categories[cat - 1].category_name);
    }

    this.selectedCategories.emit(this.selected);
    console.log(this.selected);
  }
}
