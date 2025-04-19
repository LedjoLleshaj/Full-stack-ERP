import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environment/environments";
import { Sale } from "src/app/models/sale.model";

@Injectable({
  providedIn: "root",
})
export class SalesApiService {
  constructor(private http: HttpClient) {}

  getSales(): Observable<Sale[]> {
    return this.http.get<Sale[]>(`${environment.apiUrl}${environment.getSales}`);
  }

  paySale(id: number): Observable<Sale> {
    return this.http.put<Sale>(`${environment.apiUrl}${environment.paySale}+${id}`, {});
  }
}
