export interface LowStockProduct {
  id: number;
  name: string;
  category: string;
  price: number;
  quantity: number;
  reorder_level: number;
  reorder_quantity: number;
}
