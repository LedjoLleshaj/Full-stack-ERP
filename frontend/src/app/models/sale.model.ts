import { Product } from "./product.model";
export interface Sale {
  id: number;
  quantity: number;
  sale_date: string;
  prod: number;
  user: number;
  product: Product;
}
