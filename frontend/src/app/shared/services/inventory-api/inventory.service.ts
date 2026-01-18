import { Injectable } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environments/environment";
import { Inventory } from "src/app/models/inventory.model";

@Injectable({
  providedIn: "root",
})
export class InventoryService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  updateInventory(data: Inventory): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}${environment.updateInventory}`, data);
  }
}
