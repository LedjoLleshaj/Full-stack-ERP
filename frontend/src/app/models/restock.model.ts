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
