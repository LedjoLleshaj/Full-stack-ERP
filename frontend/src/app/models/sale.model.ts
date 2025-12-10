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
