import { Component, OnInit, ViewChild } from "@angular/core";
import { MatPaginator } from "@angular/material/paginator";
import { MatSort } from "@angular/material/sort";
import { MatTableDataSource } from "@angular/material/table";
import { ProductService } from "../shared/services/product-api/product.service";
import { Product } from "../models/product.model";
import { MatDialog } from "@angular/material/dialog";
import { ProductBuyDialogComponent } from "../shared/components/dialogs/product-buy-dialog/product-buy-dialog.component";

@Component({
  selector: "app-products-view",
  templateUrl: "./products-view.component.html",
  styleUrls: ["./products-view.component.scss"],
})
export class ProductsViewComponent implements OnInit {
  dataSource: MatTableDataSource<Product> = new MatTableDataSource();
  displayedColumns: string[] = ["name", "category", "price", "disponibility", "description", "buy"];
  categories: string[] = [];
  activeCategory: string | null = null;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(private productService: ProductService, private dialog: MatDialog) {}

  ngOnInit() {
    this.fetchCategories();
  }

  fetchCategories() {
    this.productService.getProductCategories().subscribe((categories) => {
      this.categories = categories.map((category) => category.category_name);
    });
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
    if (this.dataSource.paginator) this.dataSource.paginator.firstPage();
  }

  filterByCategories(category: string[]) {
    // filter the data source by categories id in the inoput array

    if (this.categories.length === 0) {
      this.productService.getProducts().subscribe((products) => {
        this.dataSource = new MatTableDataSource(products);
        this.dataSource.paginator = this.paginator;
      });
    }

    this.productService.filterByCategories(category).subscribe((products) => {
      this.dataSource = new MatTableDataSource(products);
      this.dataSource.paginator = this.paginator;
    });
  }

  buyProductButton(product: Product) {
    const dialogRef = this.dialog.open(ProductBuyDialogComponent, {
      data: product,
    });

    dialogRef.afterClosed().subscribe((result) => {
      console.log("The dialog was closed", result);
    });
  }
}
