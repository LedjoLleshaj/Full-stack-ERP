export interface PaymentTerms {
  id: number;
  name: string;
  days: number;
  description: string;
  is_active: boolean;
}

export interface AgingBucketEntry {
  id: number;
  invoice_number: string | null;
  transaction_type: string;
  client: string | null;
  supplier: string | null;
  total_amount: string;
  currency: string;
  due_date: string;
  days_overdue: number;
  status: string;
}

export interface AgingBucketSummary {
  count: number;
  total: number;
}

export interface AgingReport {
  buckets: {
    current: AgingBucketEntry[];
    '1_30': AgingBucketEntry[];
    '31_60': AgingBucketEntry[];
    '61_90': AgingBucketEntry[];
    over_90: AgingBucketEntry[];
  };
  summary: {
    current: AgingBucketSummary;
    '1_30': AgingBucketSummary;
    '31_60': AgingBucketSummary;
    '61_90': AgingBucketSummary;
    over_90: AgingBucketSummary;
  };
}
