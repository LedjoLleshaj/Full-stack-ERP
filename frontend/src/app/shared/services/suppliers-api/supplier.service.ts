import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environments/environment";
import { Supplier } from "src/app/models/supplier.model";

@Injectable({
  providedIn: "root",
})
export class SupplierService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getSuppliers(): Observable<Supplier[]> {
    return this.http.get<Supplier[]>(`${this.apiUrl}/suppliers`);
  }

  getSupplier(id: number): Observable<Supplier> {
    return this.http.get<Supplier>(`${this.apiUrl}/supplier/${id}`);
  }

  getSupplierById(id: number): Observable<Supplier> {
    return this.getSupplier(id);
  }

  addSupplier(supplier: Supplier): Observable<Supplier> {
    return this.http.post<Supplier>(`${this.apiUrl}/add-supplier`, supplier);
  }

  updateSupplier(id: number, supplier: Supplier): Observable<Supplier> {
    return this.http.put<Supplier>(`${this.apiUrl}/update-supplier/${id}`, supplier);
  }

  deleteSupplier(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/delete-supplier/${id}`);
  }

  getRestocksBySupplier(supplierId: number): Observable<SupplierRestock[]> {
    return this.http.get<SupplierRestock[]>(`${this.apiUrl}/restocks-by-supplier/${supplierId}`);
  }

  getAllRestocksBySupplier(supplierId: number): Observable<SupplierRestock[]> {
    return this.http.get<SupplierRestock[]>(`${this.apiUrl}/restocks-by-supplier/${supplierId}?all=true`);
  }

  getRestockDetails(restockId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/restock/${restockId}`);
  }

  payRestock(restockId: number, payment: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/pay-restock/${restockId}`, payment);
  }
}

export interface SupplierRestock {
  id: number;
  date: string;
  product_name: string;
  product_category: string;
  quantity: number;
  price: number;
  currency: string;
  status: string;
  transaction_id: number | null;
}

