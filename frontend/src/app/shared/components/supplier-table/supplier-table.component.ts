import { Component, Input, OnInit, ViewChild } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Router } from "@angular/router";
import { MatPaginator, MatPaginatorModule } from "@angular/material/paginator";
import { MatSort, MatSortModule } from "@angular/material/sort";
import { MatTableDataSource, MatTableModule } from "@angular/material/table";
import { SupplierService } from "../../services/suppliers-api/supplier.service";
import { Supplier } from "src/app/models/supplier.model";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";

@Component({
  selector: "app-supplier-table",
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: "./supplier-table.component.html",
  styleUrls: ["./supplier-table.component.scss"],
})
export class SupplierTableComponent implements OnInit {
  @Input() dataSource!: MatTableDataSource<Supplier>;
  @Input() displayedColumns!: string[];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(private supplierService: SupplierService, public router: Router) {}

  ngOnInit() {
    this.fetchSuppliers();
  }

  fetchSuppliers() {
    this.supplierService.getSuppliers().subscribe((data) => {
      this.dataSource.data = data;
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    });
  }

  goToSupplierDetails(supplierId: number): void {
    this.router.navigate(['/supplier', supplierId]);
  }
}
