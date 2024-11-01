import { Component, EventEmitter, Input, OnInit, Output, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ProductService } from '../../services/product-api/product.service';
import { Product } from 'src/app/models/product.model';
import { ProductDetailDialogComponent } from '../dialogs/product-detail-dialog/product-detail-dialog.component';
import { MatDialog } from '@angular/material/dialog';

@Component({
  selector: 'app-product-table',
  templateUrl: './product-table.component.html',
  styleUrls: ['./product-table.component.scss']
})
export class ProductTableComponent implements OnInit {
  @Output() buyProduct = new EventEmitter<Product>();
  @Input() dataSource!: MatTableDataSource<Product>; 
  @Input() displayedColumns!: string[];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(private productService: ProductService, private dialog: MatDialog) {}

  ngOnInit() {
    this.fetchProducts();
  }

  fetchProducts() {
    this.productService.getProducts().subscribe(data => {
      this.dataSource.data = data;
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    });
  }

  openProductDetail(product: Product) {
    const dialogRef = this.dialog.open(ProductDetailDialogComponent, { data: product });
    dialogRef.afterClosed().subscribe(result => {
      console.log('The dialog was closed', result);
    });
  }

  // Emit buyProduct event when Buy button is clicked
  onBuyProduct(product: Product) {
    this.buyProduct.emit(product);
  }
}
