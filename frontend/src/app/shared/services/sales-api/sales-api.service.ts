import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environment/environments";
import { Sale, SaleResponse, SaleCreateResponse, PaymentRequest, PaymentResponse, SaleDetails } from "src/app/models/sale.model";

@Injectable({
  providedIn: "root",
})
export class SalesApiService {
  constructor(private http: HttpClient) {}

  getSales(): Observable<SaleResponse[]> {
    return this.http.get<SaleResponse[]>(`${environment.apiUrl}${environment.getSales}`);
  }

  /**
   * Add a payment to a sale's transaction
   * @param saleId - ID of the sale
   * @param payment - Payment details
   */
  paySale(saleId: number, payment: PaymentRequest): Observable<PaymentResponse> {
    return this.http.post<PaymentResponse>(
      `${environment.apiUrl}${environment.paySale}${saleId}`,
      payment
    );
  }

  checkdisponibility(productId: number): Observable<any> {
    return this.http.get<any>(`${environment.apiUrl}${environment.checkdisponibility}${productId}`);
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
    return this.http.post<SaleCreateResponse>(`${environment.apiUrl}${environment.createSale}`, sale);
  }

  getLastSoldPrice(clientId: number, productId: number): Observable<{ price: number | null; currency: string | null }> {
    return this.http.get<{ price: number | null; currency: string | null }>(
      `${environment.apiUrl}${environment.getLastSoldPrice}?client_id=${clientId}&product_id=${productId}`
    );
  }

  getSalesReport(startDate?: string, endDate?: string): Observable<any[]> {
    let url = `${environment.apiUrl}${environment.salesReport}`;
    const params: string[] = [];

    if (startDate) {
      params.push(`start_date=${startDate}`);
    }
    if (endDate) {
      params.push(`end_date=${endDate}`);
    }

    if (params.length > 0) {
      url += `?${params.join("&")}`;
    }


    return this.http.get<any[]>(url);
  }

  /**
   * Get detailed sale information including transaction and payment history
   * @param saleId - ID of the sale
   */
  getSaleDetails(saleId: number): Observable<SaleDetails> {
    return this.http.get<SaleDetails>(
      `${environment.apiUrl}${environment.getSaleDetails}${saleId}`
    );
  }
}

