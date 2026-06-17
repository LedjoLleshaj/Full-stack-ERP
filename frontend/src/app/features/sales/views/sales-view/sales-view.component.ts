import { Component, OnInit, OnDestroy } from "@angular/core";
import { FormControl } from "@angular/forms";
import { SaleListRow } from "../../../../models/sale.model";
import { SalesApiService } from "../../../../shared/services/sales-api/sales-api.service";
import { ExcelExportService } from "../../../../shared/services/excel-export/excel-export.service";

@Component({
  selector: "app-sales-view",
  templateUrl: "./sales-view.component.html",
})
export class SalesViewComponent implements OnInit, OnDestroy {
  data: SaleListRow[] = [];
  total: number = 0;
  periodicUpdate: any;
  
  // Date range controls
  startDateControl = new FormControl();
  endDateControl = new FormControl();
  isExporting = false;

  constructor(
    private saleApiService: SalesApiService,
    private excelExport: ExcelExportService
  ) {}

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

  async exportToExcel() {
    this.isExporting = true;

    const startDate = this.startDateControl.value
      ? this.formatDate(this.startDateControl.value)
      : undefined;
    const endDate = this.endDateControl.value
      ? this.formatDate(this.endDateControl.value)
      : undefined;

    this.saleApiService.getSalesReport(startDate, endDate).subscribe({
      next: async (data) => {
        if (data.length === 0) {
          alert('Nuk ka të dhëna për këtë periudhë');
          this.isExporting = false;
          return;
        }
        const filename = `raporti_shitjeve_${new Date().toISOString().split('T')[0]}.xlsx`;
        await this.excelExport.downloadExcel(data, 'Raporti i Shitjeve', filename);
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

  ngOnDestroy() {
    clearInterval(this.periodicUpdate);
  }
}
