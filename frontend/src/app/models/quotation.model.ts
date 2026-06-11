export interface QuotationItem {
  id?: number;
  product: number;
  product_name?: string;
  quantity: number;
  unit_price: number;
  tax_rate?: number | null;
  tax_rate_name?: string | null;
  tax_amount?: number;
  subtotal?: number;
  line_total?: number;
}

export interface Quotation {
  id: number;
  client: number;
  client_name: string;
  status: QuotationStatus;
  currency: string;
  valid_until: string;
  notes: string;
  created_date: string;
  created_by?: number;
  created_by_name?: string;
  converted_transaction?: number | null;
  items?: QuotationItem[];
  total_amount: number;
  item_count?: number;
}

export type QuotationStatus = 'DRAFT' | 'SENT' | 'ACCEPTED' | 'REJECTED' | 'EXPIRED' | 'CONVERTED';

export interface QuotationCreatePayload {
  client: number;
  currency: string;
  valid_until: string;
  notes: string;
  items: QuotationItem[];
}

export interface ConvertResponse {
  message: string;
  quotation_id: number;
  transaction_id: number;
  total_amount: number;
}
