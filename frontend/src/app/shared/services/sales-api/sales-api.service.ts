import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environments/environment";
import { Sale, SaleResponse, SaleCreateResponse, PaymentRequest, PaymentResponse, SaleDetails, SaleUpdateResponse, SaleDeleteResponse } from "src/app/models/sale.model";
import { BaseApiService } from "../base-api.service";

@Injectable({
  providedIn: "root",
})
export class SalesApiService extends BaseApiService {
  constructor(http: HttpClient) {
    super(http);
  }

  getSales(): Observable<SaleResponse[]> {
    return this.http.get<SaleResponse[]>(`${this.apiUrl}${environment.getSales}`);
  }

  /**
   * Add a payment to a sale's transaction
   * @param saleId - ID of the sale
   * @param payment - Payment details
   */
  paySale(saleId: number, payment: PaymentRequest): Observable<PaymentResponse> {
    return this.http.post<PaymentResponse>(
      `${this.apiUrl}${environment.paySale}${saleId}`,
      payment
    );
  }

  checkdisponibility(productId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}${environment.checkdisponibility}${productId}`);
  }

  /**
   * Create a new sale with optional payment
   * @param sale - Sale data including client_id and optional payment
   */
  createSale(sale: Sale): Observable<SaleCreateResponse> {
    // make sure there is enough stock
    this.checkdisponibility(sale.prod).subscribe((response) => {
      if (response.disponibility < sale.quantity) {
        console.error("Not enough stock available");
        return;
      }
    });
    // Proceed to create the sale
    console.log("Creating sale", sale);
    return this.http.post<SaleCreateResponse>(`${this.apiUrl}${environment.createSale}`, sale);
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

  /**
   * Get detailed sale information including transaction and payment history
   * @param saleId - ID of the sale
   */
  getSaleDetails(saleId: number): Observable<SaleDetails> {
    return this.http.get<SaleDetails>(
      `${this.apiUrl}${environment.getSaleDetails}${saleId}`
    );
  }

  /**
   * Update an existing sale
   * @param saleId - ID of the sale to update
   * @param saleData - Updated sale data
   */
  updateSale(saleId: number, saleData: Partial<Sale>): Observable<SaleUpdateResponse> {
    return this.http.put<SaleUpdateResponse>(
      `${this.apiUrl}/update-sale/${saleId}`,
      saleData
    );
  }

  /**
   * Delete a sale
   * @param saleId - ID of the sale to delete
   */
  deleteSale(saleId: number): Observable<SaleDeleteResponse> {
    return this.http.delete<SaleDeleteResponse>(
      `${this.apiUrl}/delete-sale/${saleId}`
    );
  }

}
