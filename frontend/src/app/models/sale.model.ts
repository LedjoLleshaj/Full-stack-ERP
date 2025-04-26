import { Product } from "./product.model";
export interface SaleResponse {
  id: number;
  quantity: number;
  sale_date: string;
  prod: number;
  prod_price: number;
  is_paid: boolean;
  user: number;
  client: {
    name: string;
    phone: string;
    address: string;
  };
  product: Product;
}

export interface Sale {
  prod: number;
  prod_price: number;
  is_paid: boolean;
  user: number;
  client: number;
  quantity: number;
}
