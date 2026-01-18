import { Injectable } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environments/environment";
import { RestockResponse, RestockReportRow } from "src/app/models/restock.model";
import { map } from "rxjs/operators";

@Injectable({
  providedIn: "root",
})
export class RestocksApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getRestocks(): Observable<RestockResponse[]> {
    return this.http.get<RestockResponse[]>(`${this.apiUrl}/restocks`);
  }

  getRestock(id: number): Observable<RestockResponse> {
    return this.http.get<RestockResponse>(`${this.apiUrl}/restock/${id}`);
  }

  getRestocksReport(startDate?: string, endDate?: string): Observable<RestockReportRow[]> {
    return this.getRestocks().pipe(
      map((restocks) => {
        // Filter by date range if provided
        let filtered = restocks;
        
        if (startDate) {
          filtered = filtered.filter(r => r.restock_date >= startDate);
        }
        if (endDate) {
          // Add one day to include the end date
          const endDatePlusOne = new Date(endDate);
          endDatePlusOne.setDate(endDatePlusOne.getDate() + 1);
          const endDateStr = endDatePlusOne.toISOString().split('T')[0];
          filtered = filtered.filter(r => r.restock_date < endDateStr);
        }

        // Transform to report format
        return filtered.map(r => ({
          ID: r.id,
          Produkti: r.product_info?.name || 'N/A',
          Kategoria: r.product_info?.category || 'N/A',
          Sasia: r.quantity,
          Cmimi: parseFloat(r.restock_price),
          Totali: r.quantity * parseFloat(r.restock_price),
          Data: new Date(r.restock_date).toLocaleDateString('sq-AL'),
          Statusi: r.transaction_info?.status === 'COMPLETED' ? 'E paguar' : 
                   r.transaction_info?.status === 'PARTIAL' ? 'Pjeserisht e paguar' : 'Nuk eshte paguar'
        }));
      })
    );
  }
}
