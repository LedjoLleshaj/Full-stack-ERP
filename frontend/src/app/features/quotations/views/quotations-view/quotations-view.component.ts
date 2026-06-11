import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { QuotationApiService } from 'src/app/shared/services/quotation-api/quotation-api.service';
import { Quotation, QuotationStatus } from 'src/app/models/quotation.model';
import { AuthApiService } from 'src/app/shared/services/auth-api/auth-api.service';

@Component({
  selector: 'app-quotations-view',
  templateUrl: './quotations-view.component.html',
  styleUrls: ['./quotations-view.component.scss'],
})
export class QuotationsViewComponent implements OnInit {
  displayedColumns: string[] = ['id', 'client_name', 'total_amount', 'currency', 'status', 'valid_until', 'created_date', 'actions'];
  dataSource = new MatTableDataSource<Quotation>();
  isLoading = true;
  statusFilter: string = '';
  statuses: string[] = ['', 'DRAFT', 'SENT', 'ACCEPTED', 'REJECTED', 'EXPIRED', 'CONVERTED'];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private quotationService: QuotationApiService,
    private router: Router,
    private snackBar: MatSnackBar,
    public authService: AuthApiService,
  ) {}

  ngOnInit(): void {
    this.loadQuotations();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  loadQuotations(): void {
    this.isLoading = true;
    const status = this.statusFilter || undefined;
    this.quotationService.getQuotations(status).subscribe({
      next: (data) => {
        this.dataSource.data = data;
        this.isLoading = false;
      },
      error: (err) => {
        this.snackBar.open('Gabim në ngarkimin e ofertave', 'Mbyll', { duration: 5000 });
        this.isLoading = false;
      },
    });
  }

  onStatusFilterChange(): void {
    this.loadQuotations();
  }

  applyFilter(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.dataSource.filter = value.trim().toLowerCase();
  }

  viewDetails(id: number): void {
    this.router.navigate(['/quotations', id]);
  }

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      DRAFT: 'Draft',
      SENT: 'Dërguar',
      ACCEPTED: 'Pranuar',
      REJECTED: 'Refuzuar',
      EXPIRED: 'Skaduar',
      CONVERTED: 'Konvertuar',
    };
    return labels[status] || status;
  }

  getStatusClass(status: string): string {
    return `status-${status.toLowerCase()}`;
  }

  formatCurrency(amount: number, currency: string): string {
    const symbols: Record<string, string> = { EUR: '€', USD: '$', LEK: 'Lek' };
    return `${Number(amount).toFixed(2)} ${symbols[currency] || currency}`;
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('sq-AL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }
}
