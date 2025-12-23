import { Component, ViewChild } from "@angular/core";
import { MatPaginator } from "@angular/material/paginator";
import { MatSort } from "@angular/material/sort";
import { MatTableDataSource } from "@angular/material/table";
import { SupplierService } from "../../shared/services/suppliers-api/supplier.service";
import { Supplier } from "../../models/supplier.model";

@Component({
  selector: "app-supplier-view",
  templateUrl: "./supplier-view.component.html",
  styleUrls: ["./supplier-view.component.scss"],
})
export class SupplierViewComponent {
  dataSource: MatTableDataSource<Supplier> = new MatTableDataSource();
  displayedColumns: string[] = ["firstname", "lastname", "phone", "email", "address"];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(private supplierService: SupplierService) {}

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
    if (this.dataSource.paginator) this.dataSource.paginator.firstPage();
  }
}
