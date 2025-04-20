export interface Product {
  id?: number;
  name: string;
  category: string;
  price: number;
  description: string;
  disponibility: number;
  selectedQuantity?: number;
}
