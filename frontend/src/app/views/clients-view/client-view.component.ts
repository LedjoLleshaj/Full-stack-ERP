import { Component, OnInit, ViewChild } from "@angular/core";
import { MatPaginator } from "@angular/material/paginator";
import { MatSort } from "@angular/material/sort";
import { MatTableDataSource } from "@angular/material/table";
import { ClientService } from "../../shared/services/clients-api/client.service";
import { MatDialog } from "@angular/material/dialog";
import { Client } from "../../models/client.model";

@Component({
  selector: "app-client-view",
  templateUrl: "./client-view.component.html",
  styleUrls: ["./client-view.component.scss"],
})
export class ClientViewComponent {
  dataSource: MatTableDataSource<Client> = new MatTableDataSource();
  displayedColumns: string[] = ["firstname", "lastname", "phone", "address", "balance"]; //shto balancen per cdo klient

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(private clientService: ClientService) {}

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
    if (this.dataSource.paginator) this.dataSource.paginator.firstPage();
  }
}
