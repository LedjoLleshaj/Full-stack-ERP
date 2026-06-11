import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { QuotationApiService } from 'src/app/shared/services/quotation-api/quotation-api.service';
import { InvoiceService } from 'src/app/shared/services/invoice/invoice.service';
import { Quotation, QuotationStatus } from 'src/app/models/quotation.model';
import { AuthApiService } from 'src/app/shared/services/auth-api/auth-api.service';
import { DeleteConfirmationDialogComponent } from 'src/app/shared/components/delete-confirmation-dialog/delete-confirmation-dialog.component';

@Component({
  selector: 'app-quotation-details-view',
  templateUrl: './quotation-details-view.component.html',
  styleUrls: ['./quotation-details-view.component.scss'],
})
export class QuotationDetailsViewComponent implements OnInit {
  quotationId!: number;
  quotation: Quotation | null = null;
  isLoading = true;
  errorMessage = '';
  isConverting = false;

  displayedColumns: string[] = ['product_name', 'quantity', 'unit_price', 'tax_rate_name', 'tax_amount', 'line_total'];

  statusActions: { status: string; label: string; icon: string; color: string }[] = [
    { status: 'SENT', label: 'Shëno si Dërguar', icon: 'send', color: 'primary' },
    { status: 'ACCEPTED', label: 'Prano', icon: 'check_circle', color: 'primary' },
    { status: 'REJECTED', label: 'Refuzo', icon: 'cancel', color: 'warn' },
    { status: 'EXPIRED', label: 'Shëno si Skaduar', icon: 'schedule', color: 'accent' },
  ];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private quotationService: QuotationApiService,
    private invoiceService: InvoiceService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    public authService: AuthApiService,
  ) {}

  ngOnInit(): void {
    this.quotationId = Number(this.route.snapshot.paramMap.get('id'));
    if (this.quotationId) {
      this.loadQuotation();
    } else {
      this.errorMessage = 'ID e ofertës nuk u gjet';
      this.isLoading = false;
    }
  }

  loadQuotation(): void {
    this.isLoading = true;
    this.quotationService.getQuotation(this.quotationId).subscribe({
      next: (data) => {
        this.quotation = data;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Gabim në ngarkimin e ofertës';
        this.isLoading = false;
      },
    });
  }

  getStatusLabel(status: QuotationStatus): string {
    const labels: Record<string, string> = {
      DRAFT: 'Draft', SENT: 'Dërguar', ACCEPTED: 'Pranuar',
      REJECTED: 'Refuzuar', EXPIRED: 'Skaduar', CONVERTED: 'Konvertuar',
    };
    return labels[status] || status;
  }

  getStatusClass(status: string): string {
    return `status-${status.toLowerCase()}`;
  }

  getAvailableActions(): typeof this.statusActions {
    if (!this.quotation || this.quotation.status === 'CONVERTED') return [];
    const transitions: Record<string, string[]> = {
      DRAFT: ['SENT', 'ACCEPTED', 'REJECTED'],
      SENT: ['ACCEPTED', 'REJECTED', 'EXPIRED'],
      ACCEPTED: ['REJECTED'],
      REJECTED: ['DRAFT'],
      EXPIRED: ['DRAFT'],
    };
    const allowed = transitions[this.quotation.status] || [];
    return this.statusActions.filter((a) => allowed.includes(a.status));
  }

  canConvert(): boolean {
    return this.quotation?.status === 'ACCEPTED' && !this.quotation.converted_transaction;
  }

  updateStatus(newStatus: string): void {
    this.quotationService.updateStatus(this.quotationId, newStatus).subscribe({
      next: () => {
        this.snackBar.open('Statusi u përditësua', 'Mbyll', { duration: 3000 });
        this.loadQuotation();
      },
      error: (err) => {
        const msg = err?.error?.error || 'Gabim në ndryshimin e statusit';
        this.snackBar.open(msg, 'Mbyll', { duration: 5000 });
      },
    });
  }

  convertToSale(): void {
    if (!this.canConvert()) return;
    this.isConverting = true;
    this.quotationService.convertToSale(this.quotationId).subscribe({
      next: (result) => {
        this.isConverting = false;
        this.snackBar.open(
          `Oferta u konvertua në shitje! Transaksioni #${result.transaction_id}`,
          'Shiko', { duration: 6000 }
        ).onAction().subscribe(() => {
          this.router.navigate(['/sales']);
        });
        this.loadQuotation();
      },
      error: (err) => {
        this.isConverting = false;
        const msg = err?.error?.error || 'Gabim në konvertimin e ofertës';
        this.snackBar.open(msg, 'Mbyll', { duration: 5000 });
      },
    });
  }

  onDelete(): void {
    if (!this.quotation) return;
    const dialogRef = this.dialog.open(DeleteConfirmationDialogComponent, {
      width: '400px',
      data: {
        title: 'Fshi Ofertën?',
        message: `Je i sigurt që dëshiron të fshish ofertën QUO-${String(this.quotation.id).padStart(6, '0')}?`,
        itemDetails: {
          Klienti: this.quotation.client_name,
          Totali: this.formatCurrency(this.quotation.total_amount, this.quotation.currency),
        },
      },
    });

    dialogRef.afterClosed().subscribe((confirmed) => {
      if (confirmed) {
        this.quotationService.deleteQuotation(this.quotationId).subscribe({
          next: () => {
            this.snackBar.open('Oferta u fshi', 'Mbyll', { duration: 3000 });
            this.router.navigate(['/quotations']);
          },
          error: (err) => {
            const msg = err?.error?.error || 'Gabim në fshirjen e ofertës';
            this.snackBar.open(msg, 'Mbyll', { duration: 5000 });
          },
        });
      }
    });
  }

  formatCurrency(amount: number | string, currency: string): string {
    const num = typeof amount === 'string' ? parseFloat(amount) : amount;
    const symbols: Record<string, string> = { EUR: '€', USD: '$', LEK: 'Lek' };
    return `${num.toFixed(2)} ${symbols[currency] || currency}`;
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('sq-AL', {
      year: 'numeric', month: 'long', day: 'numeric',
    });
  }

  formatDateTime(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('sq-AL', {
      year: 'numeric', month: 'long', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  goBack(): void {
    this.router.navigate(['/quotations']);
  }
}
