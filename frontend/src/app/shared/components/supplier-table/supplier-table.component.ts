import { Component, Input, OnInit, ViewChild } from "@angular/core";
import { Router } from "@angular/router";
import { MatPaginator } from "@angular/material/paginator";
import { MatSort } from "@angular/material/sort";
import { MatTableDataSource } from "@angular/material/table";
import { SupplierService } from "../../services/suppliers-api/supplier.service";
import { Supplier } from "src/app/models/supplier.model";

@Component({
  selector: "app-supplier-table",
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
}
