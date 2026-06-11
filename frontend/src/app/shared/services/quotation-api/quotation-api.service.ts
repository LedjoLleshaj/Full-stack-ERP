import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BaseApiService } from '../base-api.service';
import {
  Quotation,
  QuotationCreatePayload,
  ConvertResponse,
} from 'src/app/models/quotation.model';

@Injectable({
  providedIn: 'root',
})
export class QuotationApiService extends BaseApiService {
  constructor(http: HttpClient) {
    super(http);
  }

  getQuotations(status?: string): Observable<Quotation[]> {
    const params = this.createParams({ status });
    return this.http.get<Quotation[]>(`${this.apiUrl}/quotations`, { params });
  }

  getQuotation(id: number): Observable<Quotation> {
    return this.http.get<Quotation>(`${this.apiUrl}/quotation/${id}`);
  }

  createQuotation(data: QuotationCreatePayload): Observable<Quotation> {
    return this.http.post<Quotation>(`${this.apiUrl}/create-quotation`, data);
  }

  updateQuotation(id: number, data: Partial<QuotationCreatePayload>): Observable<Quotation> {
    return this.http.put<Quotation>(`${this.apiUrl}/update-quotation/${id}`, data);
  }

  deleteQuotation(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/delete-quotation/${id}`);
  }

  updateStatus(id: number, status: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/quotation/${id}/status`, { status });
  }

  convertToSale(id: number): Observable<ConvertResponse> {
    return this.http.post<ConvertResponse>(`${this.apiUrl}/quotation/${id}/convert`, {});
  }
}
