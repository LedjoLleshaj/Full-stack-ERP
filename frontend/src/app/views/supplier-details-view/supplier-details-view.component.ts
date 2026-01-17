import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Supplier } from 'src/app/models/supplier.model';
import { SupplierService, SupplierRestock } from 'src/app/shared/services/suppliers-api/supplier.service';
import * as XLSX from 'xlsx';

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
  isExporting = false;
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
      'LEK': 'Lek'
    };
    return `${amount.toFixed(2)} ${symbols[currency] || currency}`;
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

  goToRestock(restockId: number): void {
    this.router.navigate(['/restock', restockId]);
  }

  exportToExcel(): void {
    if (!this.supplier) return;
    
    this.isExporting = true;
    const supplierId = this.supplier.id;
    const supplierName = `${this.supplier.firstname}_${this.supplier.lastname}`.replace(/\s+/g, '_');
    
    // Fetch ALL restocks for this supplier (not just the displayed 10)
    this.supplierService.getAllRestocksBySupplier(supplierId!).subscribe({
      next: (allRestocks) => {
        // Transform restocks to export format
        //add autoincrement number
        let num = 1;
        const exportData = allRestocks.map(r => ({
          'Num': num++,
          'ID': r.id,
          'Data': this.formatDate(r.date),
          'Produkti': r.product_name,
          'Kategoria': r.product_category,
          'Sasia (kg)': r.quantity,
          'Cmimi': r.price,
          'Valuta': r.currency,
          'Totali': (r.quantity * r.price).toFixed(2),
          'Statusi': this.getStatusLabel(r.status)
        }));

        if (exportData.length === 0) {
          this.snackBar.open('Nuk ka furnizime për të eksportuar', 'Mbyll', { duration: 3000 });
          this.isExporting = false;
          return;
        }

        // Create workbook and worksheet
        const worksheet = XLSX.utils.json_to_sheet(exportData);
        const workbook = XLSX.utils.book_new();
        
        // Auto-size columns
        const columnWidths = this.getColumnWidths(exportData);
        worksheet['!cols'] = columnWidths;
        
        // Add worksheet to workbook
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Furnizimet');
        
        // Generate filename with supplier name and date
        const filename = `furnizime_${supplierName}_${new Date().toISOString().split('T')[0]}.xlsx`;
        
        // Write and download
        XLSX.writeFile(workbook, filename);
        
        this.isExporting = false;
        this.snackBar.open('Raporti u shkarkua me sukses', 'Mbyll', { duration: 3000 });
      },
      error: (err) => {
        console.error('Failed to export restocks:', err);
        this.snackBar.open('Gabim gjatë eksportimit', 'Mbyll', { duration: 3000 });
        this.isExporting = false;
      }
    });
  }

  private getColumnWidths(data: any[]): { wch: number }[] {
    if (!data || data.length === 0) return [];
    
    const headers = Object.keys(data[0]);
    return headers.map(header => {
      const maxLength = Math.max(
        header.length,
        ...data.map(row => String(row[header] || '').length)
      );
      return { wch: Math.min(maxLength + 2, 50) };
    });
  }
}
