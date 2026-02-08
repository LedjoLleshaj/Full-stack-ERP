import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environments/environment";
import { BaseApiService } from "../base-api.service";

export interface PaymentUpdateResult {
  payment_id: number;
  transaction_status: string;
  total_paid: number;
}

export interface PaymentDeleteResult {
  message: string;
  transaction_status: string;
  total_paid: number;
}

@Injectable({
  providedIn: "root",
})
export class PaymentApiService extends BaseApiService {
  constructor(http: HttpClient) {
    super(http);
  }

  /**
   * Update an existing payment
   * @param paymentId - ID of the payment to update
   * @param data - Updated payment data (amount, notes)
   */
  updatePayment(paymentId: number, data: { amount: number; currency: string; notes: string }): Observable<PaymentUpdateResult> {
    return this.http.put<PaymentUpdateResult>(`${this.apiUrl}/update-payment/${paymentId}`, data);
  }

  /**
   * Delete a payment
   * @param paymentId - ID of the payment to delete
   */
  deletePayment(paymentId: number): Observable<PaymentDeleteResult> {
    return this.http.delete<PaymentDeleteResult>(`${this.apiUrl}/delete-payment/${paymentId}`);
  }
}
