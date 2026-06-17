import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environments/environment";
import {
  CreateSaleRequest,
  UpdateSaleRequest,
  SaleCreateResponse,
  SaleUpdateResponse,
  SaleDeleteResponse,
  SaleListRow,
  SaleDetails,
  PaymentRequest,
  PaymentResponse,
  ReturnRequest,
  ReturnResponse,
  ReturnInfo,
} from "src/app/models/sale.model";
import { BaseApiService } from "../base-api.service";

@Injectable({
  providedIn: "root",
})
export class SalesApiService extends BaseApiService {
  constructor(http: HttpClient) {
    super(http);
  }

  getSales(): Observable<SaleListRow[]> {
    return this.http.get<SaleListRow[]>(`${this.apiUrl}${environment.getSales}`);
  }

  createSale(sale: CreateSaleRequest): Observable<SaleCreateResponse> {
    return this.http.post<SaleCreateResponse>(
      `${this.apiUrl}${environment.createSale}`,
      sale
    );
  }

  updateSale(transactionId: number, data: UpdateSaleRequest): Observable<SaleUpdateResponse> {
    return this.http.put<SaleUpdateResponse>(
      `${this.apiUrl}${environment.updateSale}${transactionId}`,
      data
    );
  }

  deleteSale(transactionId: number): Observable<SaleDeleteResponse> {
    return this.http.delete<SaleDeleteResponse>(
      `${this.apiUrl}${environment.deleteSale}${transactionId}`
    );
  }

  getSaleDetails(transactionId: number): Observable<SaleDetails> {
    return this.http.get<SaleDetails>(
      `${this.apiUrl}${environment.getSaleDetails}${transactionId}`
    );
  }

  paySale(transactionId: number, payment: PaymentRequest): Observable<PaymentResponse> {
    return this.http.post<PaymentResponse>(
      `${this.apiUrl}${environment.paySale}${transactionId}`,
      payment
    );
  }

  getLastSoldPrice(clientId: number, productId: number): Observable<{ price: number | null; currency: string | null }> {
    const params = this.createParams({ client_id: clientId, product_id: productId });
    return this.http.get<{ price: number | null; currency: string | null }>(
      `${this.apiUrl}${environment.getLastSoldPrice}`,
      { params }
    );
  }

  getSalesReport(startDate?: string, endDate?: string): Observable<any[]> {
    const params = this.createParams({ start_date: startDate, end_date: endDate });
    return this.http.get<any[]>(`${this.apiUrl}${environment.salesReport}`, { params });
  }

  createReturn(transactionId: number, data: ReturnRequest): Observable<ReturnResponse> {
    return this.http.post<ReturnResponse>(
      `${this.apiUrl}${environment.createReturn}${transactionId}`,
      data
    );
  }

  getSaleReturns(transactionId: number): Observable<ReturnInfo[]> {
    return this.http.get<ReturnInfo[]>(
      `${this.apiUrl}${environment.getSaleReturns}${transactionId}`
    );
  }

  checkdisponibility(productId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}${environment.checkdisponibility}${productId}`);
  }
}
