import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { PaymentTerms, AgingReport } from '../../../models/payment-terms.model';
import { TransactionInfo } from '../../../models/sale.model';
import { BaseApiService } from '../base-api.service';

@Injectable({
  providedIn: 'root',
})
export class PaymentTermsApiService extends BaseApiService {
  constructor(http: HttpClient) {
    super(http);
  }

  getPaymentTerms(): Observable<PaymentTerms[]> {
    return this.http
      .get<{ results: PaymentTerms[] }>(`${this.apiV1Url}/payment-terms/`)
      .pipe(map((response) => response.results));
  }

  getOverdueTransactions(): Observable<TransactionInfo[]> {
    return this.http.get<TransactionInfo[]>(
      `${this.apiV1Url}/transactions/overdue/`
    );
  }

  getAgingReport(): Observable<AgingReport> {
    return this.http.get<AgingReport>(
      `${this.apiV1Url}/transactions/aging-report/`
    );
  }
}
