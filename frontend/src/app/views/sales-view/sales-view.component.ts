import { Component, OnInit, OnDestroy } from "@angular/core";
import { FormControl } from "@angular/forms";
import { Sale, SaleResponse } from "../../models/sale.model";
import { SalesApiService } from "../../shared/services/sales-api/sales-api.service";

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

  exportToCSV() {
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

        // Convert JSON to CSV
        const csv = this.convertToCSV(data);
        
        // Create blob and download
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `sales_report_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
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

  private convertToCSV(data: any[]): string {
    if (!data || data.length === 0) {
      return '';
    }

    // Get headers from first object
    const headers = Object.keys(data[0]);
    
    // Create CSV header row
    const csvHeaders = headers.join(',');
    
    // Create CSV data rows
    const csvRows = data.map(row => {
      return headers.map(header => {
        const value = row[header];
        // Escape values containing commas or quotes
        if (value === null || value === undefined) {
          return '';
        }
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(',');
    });
    
    // Combine headers and rows
    return [csvHeaders, ...csvRows].join('\n');
  }

  ngOnDestroy() {
    clearInterval(this.periodicUpdate);
  }
}
