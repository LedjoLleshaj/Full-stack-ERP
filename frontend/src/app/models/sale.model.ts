import { Product } from "./product.model";

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
  payment_status: string; // PENDING, PARTIAL, COMPLETED
}

export interface Sale {
  prod: number;
  prod_price: number;
  user: number;
  client_id: number; // Changed from 'client'
  quantity: number;
  currency?: string;
  payment?: PaymentData; // Optional payment info
}

export interface PaymentData {
  account_id: number;
  amount: number;
  currency: string;
  payment_method: 'CASH' | 'CARD';
  notes?: string;
}

export interface SaleCreateResponse {
  message: string;
  sale_id: number;
  transaction_id: number;
  transaction_status: string;
  total_amount: number;
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

// Detailed sale view interfaces
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
}

export interface PaymentInfo {
  id: number;
  transaction: number;
  account: number;
  amount: string;
  currency: string;
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

export interface UserInfo {
  id: number;
  firstname: string;
  lastname: string;
}

export interface SaleDetails {
  id: number;
  quantity: number;
  sale_date: string;
  prod_price: number;
  product: {
    id: number;
    name: string;
    category: string;
    price: string;
    description: string;
  };
  user?: UserInfo;
  client?: ClientInfo;
  transaction?: TransactionInfo;
  payments: PaymentInfo[];
  payment_summary?: PaymentSummary;
}
