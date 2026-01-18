import { Injectable } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environments/environment";
import { Product } from "src/app/models/product.model";
import { ProductCategory } from "src/app/models/product-category.model";
import { ProductName } from "src/app/models/product-name.model";

@Injectable({
  providedIn: "root",
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
    return this.http.get<ProductCategory[]>(`${this.apiUrl}${environment.getProductCategories}`);
  }

  updatePrice(productId: number, data: Product): Observable<Product> {
    return this.http.put<Product>(`${this.apiUrl}${environment.updatePrice}${productId}`, data);
  }

  filterByCategories(categories: string[]): Observable<Product[]> {
    const params = new HttpParams().set("categories", categories.join(","));
    return this.http.get<Product[]>(`${this.apiUrl}/filterbycategories`, { params });
  }

  getProductNames(): Observable<ProductName[]> {
    return this.http.get<ProductName[]>(`${this.apiUrl}${environment.getProductNames}`);
  }

  getProductById(productId: number): Observable<Product> {
    return this.http.get<Product>(`${this.apiUrl}${environment.productbyid}${productId}`);
  }

  getProductHistory(productId: number, months: number = 3): Observable<ProductHistory> {
    return this.http.get<ProductHistory>(`${this.apiUrl}/product-history/${productId}?months=${months}`);
  }
}

// Product history response types
export interface ProductHistory {
  product: Product & { disponibility: number };
  recent_sales: RecentSale[];
  recent_restocks: RecentRestock[];
  price_history: {
    sale_prices: PricePoint[];
    restock_prices: PricePoint[];
  };
}

export interface RecentSale {
  id: number;
  date: string;
  price: number;
  quantity: number;
  currency: string;
  client_name: string;
  transaction_id: number | null;
  status: string;
}

export interface RecentRestock {
  id: number;
  date: string;
  price: number;
  quantity: number;
  currency: string;
  supplier_name: string;
}

export interface PricePoint {
  date: string;
  price: number;
  currency: string;
}
