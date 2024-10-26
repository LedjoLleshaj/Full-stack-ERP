import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environment/environments';
import { Product } from 'src/app/models/product.model';
import { ProductCategory } from 'src/app/models/product-category.model';


@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  addProduct(productData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}${environment.addProduct}`, productData);
  }

  getProducts(): Observable<Product[]> {
    return this.http.get<Product[]>(`${this.apiUrl}${environment.getProducts}`);
  }

  getProductCategories(): Observable<ProductCategory[]> {
    return this.http.get<ProductCategory[]>(`${this.apiUrl}${environment.getCategories}`);
  }
}
