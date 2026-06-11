export interface RestockProductInfo {
  name: string;
  category: string;
  price: string;
}

export interface RestockTransactionInfo {
  id: number;
  status: string;
  total_amount: number;
  currency: string;
}

export interface RestockPayment {
  id: number;
  transaction: number;
  account: number;
  amount: string;
  currency: string;
  payment_method: string;
  payment_date: string;
  notes?: string;
}

export interface RestockResponse {
  id: number;
  quantity: number;
  restock_date: string;
  restock_price: string;
  prod: number;
  transaction: number;
  product_info: RestockProductInfo | null;
  transaction_info: RestockTransactionInfo | null;
  payments: RestockPayment[];
  tax_amount?: number;
  tax_rate_name?: string;
}

export interface RestockReportRow {
  ID: number;
  Produkti: string;
  Kategoria: string;
  Sasia: number;
  Cmimi: number;
  Totali: number;
  Data: string;
  Statusi: string;
}

export interface RestockUpdateResponse {
  message: string;
  restock_id: number;
  transaction_id: number;
  transaction_status: string;
  total_amount: number;
  total_paid: number;
  remaining: number;
}

export interface RestockDeleteResponse {
  message: string;
  restock_id: number;
  transaction_id: number;
  inventory_removed: number;
  product_name: string;
  payments_reversed: number;
  total_reversed: number;
  accounts_affected: number[];
}
