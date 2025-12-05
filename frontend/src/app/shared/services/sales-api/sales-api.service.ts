import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environment/environments";
import { Sale, SaleResponse } from "src/app/models/sale.model";

@Injectable({
  providedIn: "root",
})
export class SalesApiService {
  constructor(private http: HttpClient) {}

  getSales(): Observable<SaleResponse[]> {
    return this.http.get<SaleResponse[]>(`${environment.apiUrl}${environment.getSales}`);
  }

  paySale(id: number): Observable<Sale> {
    return this.http.put<Sale>(`${environment.apiUrl}${environment.paySale}+${id}`, {});
  }

  checkdisponibility(productId: number): Observable<any> {
    return this.http.get<any>(`${environment.apiUrl}${environment.checkdisponibility}${productId}`);
  }

  createSale(sale: Sale): Observable<Sale> {
    // make sure there is enough stock
    this.checkdisponibility(sale.prod).subscribe((response) => {
      if (response.disponibility < sale.quantity) {
        console.error("Not enough stock available");
        return;
      }
    });
    // Proceed to create the sale
    console.log("Creating sale", sale);
    return this.http.post<Sale>(`${environment.apiUrl}${environment.createSale}`, sale);
  }

  getLastSoldPrice(clientId: number, productId: number): Observable<{ price: number | null }> {
    return this.http.get<{ price: number | null }>(
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
}
