export interface Product {
  id?: number;
  name: string;
  category: string;
  price: number;
  description: string;
  disponibility: number;
  selectedQuantity?: number;
  reorder_level?: number;
  reorder_quantity?: number;
}
