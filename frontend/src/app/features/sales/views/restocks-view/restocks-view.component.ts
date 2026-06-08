import { Component, OnInit, OnDestroy } from "@angular/core";
import { FormControl } from "@angular/forms";
import { RestockResponse } from "../../../../models/restock.model";
import { RestocksApiService } from "../../../../shared/services/restocks-api/restocks-api.service";
import { ExcelExportService } from "../../../../shared/services/excel-export/excel-export.service";

@Component({
  selector: "app-restocks-view",
  templateUrl: "./restocks-view.component.html",
})
export class RestocksViewComponent implements OnInit, OnDestroy {
  data: RestockResponse[] = [];
  total: number = 0;
  periodicUpdate: any;
  
  // Date range controls
  startDateControl = new FormControl();
  endDateControl = new FormControl();
  isExporting = false;

  constructor(
    private restocksApiService: RestocksApiService,
    private excelExport: ExcelExportService
  ) {}

  ngOnInit() {
    this.fetchRestocks();
    this.periodicUpdate = setInterval(() => {
      this.fetchRestocks();
    }, 10000);
  }

  fetchRestocks() {
    this.restocksApiService.getRestocks().subscribe((data) => {
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

    this.restocksApiService.getRestocksReport(startDate, endDate).subscribe({
      next: async (data) => {
        if (data.length === 0) {
          alert('Nuk ka të dhëna për këtë periudhë');
          this.isExporting = false;
          return;
        }
        const filename = `raporti_furnizimeve_${new Date().toISOString().split('T')[0]}.xlsx`;
        await this.excelExport.downloadExcel(data as unknown as Record<string, unknown>[], 'Raporti i Furnizimeve', filename);
        this.isExporting = false;
      },
      error: (error) => {
        console.error('Error exporting restocks report:', error);
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
