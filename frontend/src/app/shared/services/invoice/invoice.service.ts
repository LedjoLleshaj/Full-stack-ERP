import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseApiService } from '../base-api.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class InvoiceService extends BaseApiService {
  constructor(http: HttpClient) {
    super(http);
  }

  downloadInvoice(transactionId: number): void {
    this.http.get(
      `${this.apiUrl}${environment.invoice}${transactionId}/invoice/`,
      { responseType: 'blob' }
    ).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `INV-${String(transactionId).padStart(6, '0')}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        console.error('Failed to download invoice:', err);
      }
    });
  }
}
