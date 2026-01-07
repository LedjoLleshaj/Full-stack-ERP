import { Component, EventEmitter, Input, OnInit, Output, ViewChild } from "@angular/core";
import { MatPaginator } from "@angular/material/paginator";
import { MatSort } from "@angular/material/sort";
import { MatTableDataSource } from "@angular/material/table";
import { Router } from "@angular/router";
import { ProductService } from "../../services/product-api/product.service";
import { Product } from "src/app/models/product.model";
import { EditPriceDialogComponent } from "../../../dialogs/edit-price-dialog/edit-price-dialog.component";
import { MatDialog } from "@angular/material/dialog";

@Component({
  selector: "app-product-table",
  templateUrl: "./product-table.component.html",
  styleUrls: ["./product-table.component.scss"],
})
export class ProductTableComponent implements OnInit {
  @Output() buyProduct = new EventEmitter<Product>();
  @Input() dataSource!: MatTableDataSource<Product>;
  @Input() displayedColumns!: string[];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private productService: ProductService,
    private dialog: MatDialog,
    private router: Router
  ) {}

  ngOnInit() {
    this.fetchProducts();
  }

  fetchProducts() {
    this.productService.getProducts().subscribe((data) => {
      this.dataSource.data = data.filter((product) => product.disponibility > 0);
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    });
  }

  openProductDetail(product: Product) {
    this.router.navigate(['/product', product.id]);
  }

  openEditPriceDialog(product: Product) {
    const dialogRef = this.dialog.open(EditPriceDialogComponent, {
      width: "300px",
      data: { ...product },
    });
    console.log("Product to edit", product);

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        console.log("Dialog result:", result);
        this.productService.updatePrice(result.id, result).subscribe((response) => {
          console.log("Price updated successfully", response);
          this.fetchProducts();
        });
      }
    });
  }

  // Emit buyProduct event when Buy button is clicked
  onBuyProduct(product: Product) {
    this.buyProduct.emit(product);
  }
}
