import { Component, OnInit, OnDestroy } from "@angular/core";
import { FormControl } from "@angular/forms";
import { Sale, SaleResponse } from "../../models/sale.model";
import { SalesApiService } from "../../shared/services/sales-api/sales-api.service";
import * as XLSX from 'xlsx';

@Component({
  selector: "app-sales-view",
  templateUrl: "./sales-view.component.html",
})
export class SalesViewComponent implements OnInit, OnDestroy {
  data: SaleResponse[] = [];
  total: number = 0;
  periodicUpdate: any;
  
  // Date range controls
  startDateControl = new FormControl();
  endDateControl = new FormControl();
  isExporting = false;

  constructor(private saleApiService: SalesApiService) {}

  ngOnInit() {
    this.fetchHistory();
    this.periodicUpdate = setInterval(() => {
      this.fetchHistory();
    }, 10000);
  }

  fetchHistory() {
    this.saleApiService.getSales().subscribe((data) => {
      this.total = data.length;
      this.data = data;
    });
  }

  exportToExcel() {
    this.isExporting = true;
    
    // Format dates to YYYY-MM-DD if they exist
    const startDate = this.startDateControl.value 
      ? this.formatDate(this.startDateControl.value) 
      : undefined;
    const endDate = this.endDateControl.value 
      ? this.formatDate(this.endDateControl.value) 
      : undefined;

    this.saleApiService.getSalesReport(startDate, endDate).subscribe({
      next: (data) => {
        if (data.length === 0) {
          alert('Nuk ka të dhëna për këtë periudhë');
          this.isExporting = false;
          return;
        }

        // Create workbook and worksheet
        const worksheet = XLSX.utils.json_to_sheet(data);
        const workbook = XLSX.utils.book_new();
        
        // Auto-size columns
        const columnWidths = this.getColumnWidths(data);
        worksheet['!cols'] = columnWidths;
        
        // Add worksheet to workbook
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Raporti i Shitjeve');
        
        // Generate filename with date
        const filename = `raporti_shitjeve_${new Date().toISOString().split('T')[0]}.xlsx`;
        
        // Write and download
        XLSX.writeFile(workbook, filename);
        
        this.isExporting = false;
      },
      error: (error) => {
        console.error('Error exporting sales report:', error);
        alert('Gabim gjatë eksportimit të raportit');
        this.isExporting = false;
      }
    });
  }

  private formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private getColumnWidths(data: any[]): { wch: number }[] {
    if (!data || data.length === 0) return [];
    
    const headers = Object.keys(data[0]);
    return headers.map(header => {
      // Find max length of content in this column (including header)
      const maxLength = Math.max(
        header.length,
        ...data.map(row => String(row[header] || '').length)
      );
      // Add some padding
      return { wch: Math.min(maxLength + 2, 50) };
    });
  }

  ngOnDestroy() {
    clearInterval(this.periodicUpdate);
  }
}
