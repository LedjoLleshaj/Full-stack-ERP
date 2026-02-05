import { Injectable } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environments/environment";
import { Product } from "src/app/models/product.model";
import { ProductCategory } from "src/app/models/product-category.model";
import { ProductName } from "src/app/models/product-name.model";

import { BaseApiService } from "../base-api.service";

@Injectable({
  providedIn: "root",
})
export class ProductService extends BaseApiService {
  constructor(http: HttpClient) {
    super(http);
  }

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
    const params = this.createParams({ months });
    return this.http.get<ProductHistory>(`${this.apiUrl}/product-history/${productId}`, { params });
  }

  /**
   * Create a new product category or return existing one
   * @param categoryName - Name of the category to create
   */
  addProductCategory(categoryName: string): Observable<{
    message: string;
    category: ProductCategory;
    created: boolean;
  }> {
    return this.http.post<{
      message: string;
      category: ProductCategory;
      created: boolean;
    }>(`${this.apiUrl}/add-product-category`, { category_name: categoryName });
  }

  /**
   * Create a new product name linked to a category
   * @param productName - Name of the product to create
   * @param categoryName - Name of the category (will be created if doesn't exist)
   */
  addProductName(productName: string, categoryName: string): Observable<{
    message: string;
    product_name: ProductName;
    category: ProductCategory;
    created: boolean;
  }> {
    return this.http.post<{
      message: string;
      product_name: ProductName;
      category: ProductCategory;
      created: boolean;
    }>(`${this.apiUrl}/add-product-name`, {
      product_name: productName,
      category_name: categoryName
    });
  }

  // ========== PRODUCT CRUD ==========

  /**
   * Update a product (name, category, price, description)
   */
  updateProduct(productId: number, data: Partial<Product>): Observable<Product> {
    return this.http.put<Product>(`${this.apiUrl}/update-product/${productId}`, data);
  }

  /**
   * Delete a product (blocked if has sales, restocks, or inventory references)
   */
  deleteProduct(productId: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/delete-product/${productId}`);
  }

  // ========== CATEGORY CRUD ==========

  /**
   * Update a product category name
   */
  updateProductCategory(categoryId: number, categoryName: string): Observable<{
    message: string;
    category: ProductCategory;
  }> {
    return this.http.put<{
      message: string;
      category: ProductCategory;
    }>(`${this.apiUrl}/update-product-category/${categoryId}`, { category_name: categoryName });
  }

  /**
   * Delete a product category (products will be reassigned)
   */
  deleteProductCategory(categoryId: number): Observable<{ message: string; products_updated: number }> {
    return this.http.delete<{ message: string; products_updated: number }>(`${this.apiUrl}/delete-product-category/${categoryId}`);
  }

  // ========== PRODUCT NAME CRUD ==========

  /**
   * Update a product name
   */
  updateProductName(nameId: number, productName: string, categoryName?: string): Observable<{
    message: string;
    product_name: ProductName;
  }> {
    const body: any = { product_name: productName };
    if (categoryName) {
      body.category_name = categoryName;
    }
    return this.http.put<{
      message: string;
      product_name: ProductName;
    }>(`${this.apiUrl}/update-product-name/${nameId}`, body);
  }

  /**
   * Delete a product name (safe, no dependencies)
   */
  deleteProductName(nameId: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/delete-product-name/${nameId}`);
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
