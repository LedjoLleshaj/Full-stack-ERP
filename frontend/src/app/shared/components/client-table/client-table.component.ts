import { Component, EventEmitter, Input, OnInit, Output, ViewChild } from "@angular/core";
import { Router } from "@angular/router";
import { MatPaginator } from "@angular/material/paginator";
import { MatSort } from "@angular/material/sort";
import { MatTableDataSource } from "@angular/material/table";
import { ClientService } from "../../services/clients-api/client.service";
import { Client } from "src/app/models/client.model";
import { MatDialog } from "@angular/material/dialog";

@Component({
  selector: "app-client-table",
  templateUrl: "./client-table.component.html",
  styleUrls: ["./client-table.component.scss"],
})
export class ClientTableComponent implements OnInit {
  @Output() openClient = new EventEmitter<Client>();
  @Input() dataSource!: MatTableDataSource<Client>;
  @Input() displayedColumns!: string[];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(private clientService: ClientService, public router: Router, private dialog: MatDialog) {}

  ngOnInit() {
    this.fetchClients();
  }

  fetchClients() {
    this.clientService.getClients().subscribe((data) => {
      this.dataSource.data = data;
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    });
  }
}
