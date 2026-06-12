import { Pipe, PipeTransform } from '@angular/core';

/**
 * Transforms payment status codes to Albanian labels.
 * Usage: {{ status | paymentStatus }}
 */
@Pipe({
  name: 'paymentStatus',
  standalone: true
})
export class PaymentStatusPipe implements PipeTransform {
  private readonly statusLabels: { [key: string]: string } = {
    'COMPLETED': 'Paguar',
    'PARTIAL': 'Pjesërisht',
    'PENDING': 'Pa Paguar',
    'CANCELLED': 'Anuluar',
    'REFUNDED': 'Rimbursuar'
  };

  private readonly statusClasses: { [key: string]: string } = {
    'COMPLETED': 'status-completed',
    'PARTIAL': 'status-partial',
    'PENDING': 'status-pending',
    'CANCELLED': 'status-cancelled',
    'REFUNDED': 'status-refunded'
  };

  transform(value: string | null | undefined, format: 'label' | 'class' = 'label'): string {
    if (!value) return format === 'label' ? 'Pa Paguar' : 'status-pending';
    
    if (format === 'class') {
      return this.statusClasses[value] || 'status-pending';
    }
    
    return this.statusLabels[value] || value;
  }
}
