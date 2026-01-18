import { Injectable } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environments/environment";
import { Inventory } from "src/app/models/inventory.model";

import { BaseApiService } from "../base-api.service";

@Injectable({
  providedIn: "root",
})
export class InventoryService extends BaseApiService {
  constructor(http: HttpClient) {
    super(http);
  }

  updateInventory(data: Inventory): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}${environment.updateInventory}`, data);
  }
}
