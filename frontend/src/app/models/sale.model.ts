import { Product } from "./product.model";

// ======== Multi-item sale creation ========

export interface SaleLineItem {
  id?: number;
  prod: number;
  prod_price: number;
  quantity: number;
  tax_rate_id?: number | null;
  discount_type?: string | null;
  discount_value?: number;
}

export interface CreateSaleRequest {
  client_id: number;
  currency: string;
  payment_terms_id?: number | null;
  items: SaleLineItem[];
  payment?: PaymentData;
}

export interface UpdateSaleRequest {
  client_id: number;
  currency: string;
  payment_terms_id?: number | null;
  items: SaleLineItem[];
}

export interface PaymentData {
  amount: number;
  currency: string;
  payment_method: 'CASH' | 'CARD';
  notes?: string;
}

// ======== API responses ========

export interface SaleCreateResponse {
  message: string;
  transaction_id: number;
  transaction_status: string;
  total_amount: number;
  payment_warning?: string | null;
  items: {
    sale_id: number;
    product_id: number;
    product_name: string;
    quantity: number;
    prod_price: number;
    tax_amount: number;
    discount_amount: number;
    line_total: number;
  }[];
}

export interface SaleUpdateResponse {
  message: string;
  transaction_id: number;
  transaction_status: string;
  total_amount: number;
  total_paid: number;
  remaining: number;
}

export interface SaleDeleteResponse {
  message: string;
  transaction_id: number;
  inventory_restored: { product_name: string; quantity: number }[];
  payments_reversed: number;
  total_reversed: number;
  accounts_affected: number[];
}

// ======== Sales list (transaction-grouped) ========

export interface SaleListRow {
  transaction_id: number;
  products: string;
  item_count: number;
  total_amount: number;
  currency: string;
  sale_date: string;
  payment_status: string;
  client: {
    id?: number;
    name: string;
    phone: string;
    address: string;
  };
}

// ======== Sale details ========

export interface SaleLineItemDetail {
  id: number;
  product: {
    id: number;
    name: string;
    category: string;
    price: string;
    description: string;
  };
  quantity: number;
  prod_price: number;
  tax_rate_name: string | null;
  tax_rate_percent: number | null;
  tax_amount: number;
  discount_type: string | null;
  discount_value: number;
  discount_amount: number;
  line_total: number;
}

export interface TransactionInfo {
  id: number;
  transaction_type: string;
  supplier?: number;
  client?: number;
  total_amount: string;
  currency: string;
  status: string;
  created_date: string;
  completed_date?: string;
  invoice_number?: string;
  notes?: string;
  payment_terms?: number | null;
  payment_terms_name?: string | null;
  payment_terms_days?: number | null;
  due_date?: string | null;
  is_overdue?: boolean;
}

export interface PaymentInfo {
  id: number;
  transaction: number;
  account: number;
  amount: string;
  currency: string;
  original_amount?: string;
  original_currency?: string;
  payment_method: string;
  payment_date: string;
  notes?: string;
}

export interface PaymentSummary {
  total_amount: number;
  total_paid: number;
  remaining: number;
  payment_count: number;
}

export interface ClientInfo {
  id: number;
  name: string;
  firstname: string;
  lastname: string;
  phone: string;
  address: string;
  city: string;
}

export interface SaleDetails {
  transaction: TransactionInfo;
  client?: ClientInfo;
  items: SaleLineItemDetail[];
  payments: PaymentInfo[];
  payment_summary: PaymentSummary;
  returns?: ReturnInfo[];
  already_returned?: { [productId: string]: number };
}

export interface PaymentRequest {
  account_id: number;
  amount: number;
  currency: string;
  payment_method: 'CASH' | 'CARD';
  notes?: string;
}

export interface PaymentResponse {
  message: string;
  payment_id: number;
  transaction_status: string;
  total_paid: number;
  remaining: number;
}

// ======== Returns ========

export interface ReturnItem {
  sale_line_id: number;
  quantity: number;
}

export interface ReturnRequest {
  items: ReturnItem[];
  refund_method: 'CASH' | 'CARD';
  refund_currency: string;
  notes?: string;
}

export interface ReturnResponse {
  message: string;
  return_transaction_id: number;
  return_value: number;
  refund_amount: number;
  inventory_restored: { product: string; quantity: number }[];
  original_transaction_status: string;
}

export interface ReturnInfo {
  id: number;
  return_date: string;
  return_value: number;
  refund_amount: number;
  items: { product_name: string; quantity: number; unit_price: number }[];
  notes?: string;
}

// Legacy — kept for backward compatibility during migration
export interface Sale {
  prod: number;
  prod_price: number;
  user: number;
  client_id: number;
  quantity: number;
  currency?: string;
  tax_rate_id?: number;
  discount_type?: string;
  discount_value?: number;
  payment?: PaymentData;
}

export interface SaleResponse {
  id: number;
  quantity: number;
  sale_date: string;
  prod: number;
  prod_price: number;
  user: number;
  transaction: number;
  client: {
    id: number;
    name: string;
    phone: string;
    address: string;
  };
  product: Product;
  payment_status: string;
  currency?: string;
  tax_amount?: number;
  tax_rate_name?: string;
  discount_type?: string | null;
  discount_value?: number;
  discount_amount?: number;
}
