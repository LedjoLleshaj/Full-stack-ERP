export type ExpenseFrequency = 'DAILY' | 'WEEKLY' | 'MONTHLY';
export type AccountType = 'CASH' | 'BANK';
export type ExpenseChargeStatus = 'POSTED' | 'REVERSED';

export interface RecurringExpense {
  id: number;
  name: string;
  category: string | null;
  description: string;
  amount: string;
  currency: string;
  account_type: AccountType;
  frequency: ExpenseFrequency;
  start_date: string;
  next_due_date: string;
  end_date: string | null;
  auto_charge: boolean;
  is_active: boolean;
  created_date: string;
}

export interface ExpenseCharge {
  id: number;
  recurring_expense: number;
  expense_name: string;
  account: number;
  account_name: string;
  amount: string;
  currency: string;
  period_date: string;
  charge_date: string;
  status: ExpenseChargeStatus;
  notes: string | null;
}

export interface RunDueSummary {
  charged: number;
  total_amount: string;
  charges: number[];
  skipped: { expense_id: number; name: string; reason: string }[];
  message?: string;
}

export type RecurringExpensePayload = Omit<
  RecurringExpense,
  'id' | 'next_due_date' | 'is_active' | 'created_date'
>;
