import { Component, Input, OnInit, ViewChild } from "@angular/core";
import { CommonModule } from "@angular/common";
import { MatPaginator, MatPaginatorModule } from "@angular/material/paginator";
import { MatSort, MatSortModule } from "@angular/material/sort";
import { MatTableDataSource, MatTableModule } from "@angular/material/table";
import { Router } from "@angular/router";
import { ProductService } from "../../services/product-api/product.service";
import { Product } from "src/app/models/product.model";
import { EditPriceDialogComponent } from "../../../dialogs/edit-price-dialog/edit-price-dialog.component";
import { MatDialog } from "@angular/material/dialog";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";

@Component({
  selector: "app-product-table",
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: "./product-table.component.html",
  styleUrls: ["./product-table.component.scss"],
})
export class ProductTableComponent implements OnInit {
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

}
