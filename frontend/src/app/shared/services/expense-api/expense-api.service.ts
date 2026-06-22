import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { BaseApiService } from '../base-api.service';
import {
  ExpenseCharge,
  RecurringExpense,
  RecurringExpensePayload,
  RunDueSummary,
} from '../../../models/expense.model';

@Injectable({ providedIn: 'root' })
export class ExpenseApiService extends BaseApiService {
  private base = `${this.apiV1Url}/recurring-expenses`;
  private chargesBase = `${this.apiV1Url}/expense-charges`;

  constructor(http: HttpClient) {
    super(http);
  }

  list(): Observable<RecurringExpense[]> {
    return this.http
      .get<{ results: RecurringExpense[] }>(`${this.base}/`)
      .pipe(map((r) => r.results));
  }

  get(id: number): Observable<RecurringExpense> {
    return this.http.get<RecurringExpense>(`${this.base}/${id}/`);
  }

  create(payload: RecurringExpensePayload): Observable<RecurringExpense> {
    return this.http.post<RecurringExpense>(`${this.base}/`, payload);
  }

  update(id: number, payload: RecurringExpensePayload): Observable<RecurringExpense> {
    return this.http.put<RecurringExpense>(`${this.base}/${id}/`, payload);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}/`);
  }

  charge(id: number): Observable<ExpenseCharge> {
    return this.http.post<ExpenseCharge>(`${this.base}/${id}/charge/`, {});
  }

  runDue(): Observable<RunDueSummary> {
    return this.http.post<RunDueSummary>(`${this.base}/run-due/`, {});
  }

  listDue(): Observable<RecurringExpense[]> {
    return this.http.get<RecurringExpense[]>(`${this.base}/due/`);
  }

  listCharges(expenseId?: number): Observable<ExpenseCharge[]> {
    const params = this.createParams({ recurring_expense: expenseId ?? null });
    return this.http
      .get<{ results: ExpenseCharge[] }>(`${this.chargesBase}/`, { params })
      .pipe(map((r) => r.results));
  }

  reverseCharge(chargeId: number): Observable<ExpenseCharge> {
    return this.http.post<ExpenseCharge>(`${this.chargesBase}/${chargeId}/reverse/`, {});
  }
}
