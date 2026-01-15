import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Supplier } from 'src/app/models/supplier.model';
import { SupplierService, SupplierRestock } from 'src/app/shared/services/suppliers-api/supplier.service';

@Component({
  selector: 'app-supplier-details-view',
  templateUrl: './supplier-details-view.component.html',
  styleUrls: ['./supplier-details-view.component.scss']
})
export class SupplierDetailsViewComponent implements OnInit {
  supplier: Supplier | null = null;
  restocks: SupplierRestock[] = [];
  isLoading = true;
  isLoadingRestocks = false;
  errorMessage = '';

  // Table columns
  restockColumns = ['date', 'product_name', 'quantity', 'price', 'status'];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private supplierService: SupplierService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    const supplierId = this.route.snapshot.paramMap.get('id');
    if (supplierId) {
      this.loadSupplier(+supplierId);
      this.loadRestocks(+supplierId);
    } else {
      this.errorMessage = 'ID e furnitorit mungon';
      this.isLoading = false;
    }
  }

  private loadSupplier(supplierId: number): void {
    this.isLoading = true;
    this.supplierService.getSupplierById(supplierId).subscribe({
      next: (data: Supplier) => {
        this.supplier = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load supplier:', err);
        this.errorMessage = 'Gabim në ngarkimin e furnitorit';
        this.isLoading = false;
        this.snackBar.open('Gabim në ngarkimin e furnitorit', 'Mbyll', { duration: 3000 });
      }
    });
  }

  private loadRestocks(supplierId: number): void {
    this.isLoadingRestocks = true;
    this.supplierService.getRestocksBySupplier(supplierId).subscribe({
      next: (data: SupplierRestock[]) => {
        this.restocks = data;
        this.isLoadingRestocks = false;
      },
      error: (err) => {
        console.error('Failed to load restocks:', err);
        this.isLoadingRestocks = false;
      }
    });
  }

  formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('sq-AL', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  formatCurrency(amount: number, currency: string): string {
    const symbols: { [key: string]: string } = {
      'EUR': '€',
      'USD': '$',
      'LEK': 'L'
    };
    return `${symbols[currency] || currency} ${amount.toFixed(2)}`;
  }

  getStatusClass(status: string): string {
    const classes: { [key: string]: string } = {
      'COMPLETED': 'status-completed',
      'PARTIAL': 'status-partial',
      'PENDING': 'status-pending',
      'CANCELLED': 'status-cancelled'
    };
    return classes[status] || 'status-pending';
  }

  getStatusLabel(status: string): string {
    const labels: { [key: string]: string } = {
      'COMPLETED': 'Paguar',
      'PARTIAL': 'Pjesërisht',
      'PENDING': 'Pa Paguar',
      'CANCELLED': 'Anuluar'
    };
    return labels[status] || status;
  }

  goBack(): void {
    this.router.navigate(['/suppliers']);
  }
}
