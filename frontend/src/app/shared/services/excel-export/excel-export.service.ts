import { Injectable } from '@angular/core';
import * as ExcelJS from 'exceljs';

@Injectable({
  providedIn: 'root',
})
export class ExcelExportService {
  async exportToExcel(
    data: Record<string, unknown>[],
    sheetName: string,
    columnWidths?: { header: string; width: number }[]
  ): Promise<Blob> {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet(sheetName);

    if (data.length === 0) {
      const buffer = await workbook.xlsx.writeBuffer();
      return new Blob([buffer], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });
    }

    const headers = Object.keys(data[0]);
    worksheet.columns = headers.map((header) => {
      const colDef: ExcelJS.Column = {
        header,
        key: header,
        width: 15,
      } as ExcelJS.Column;

      if (columnWidths) {
        const custom = columnWidths.find((c) => c.header === header);
        if (custom) {
          colDef.width = custom.width;
        }
      }

      return colDef;
    });

    const headerRow = worksheet.getRow(1);
    headerRow.font = { bold: true };
    headerRow.alignment = { horizontal: 'center' };

    data.forEach((row) => worksheet.addRow(row));

    worksheet.columns.forEach((column) => {
      if (!column || !column.eachCell) return;
      let maxLength = 0;
      column.eachCell({ includeEmpty: true }, (cell) => {
        const cellLength = cell.value ? cell.value.toString().length : 0;
        maxLength = Math.max(maxLength, cellLength);
      });
      column.width = Math.min(Math.max(maxLength + 2, 10), 50);
    });

    const buffer = await workbook.xlsx.writeBuffer();
    return new Blob([buffer], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });
  }

  async downloadExcel(
    data: Record<string, unknown>[],
    sheetName: string,
    filename: string,
    columnWidths?: { header: string; width: number }[]
  ): Promise<void> {
    const blob = await this.exportToExcel(data, sheetName, columnWidths);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  }
}
