import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { PaymentTermsApiService } from 'src/app/shared/services/payment-terms-api/payment-terms-api.service';
import {
  AgingReport,
  AgingBucketEntry,
  AgingBucketSummary,
} from '../../../../models/payment-terms.model';

interface BucketDisplay {
  key: string;
  label: string;
  entries: AgingBucketEntry[];
  summary: AgingBucketSummary;
}

@Component({
  selector: 'app-aging-report-view',
  templateUrl: './aging-report-view.component.html',
  styleUrls: ['./aging-report-view.component.scss'],
})
export class AgingReportViewComponent implements OnInit {
  isLoading = true;
  buckets: BucketDisplay[] = [];
  grandTotal = 0;
  grandCount = 0;
  displayedColumns = [
    'invoice_number',
    'client',
    'total_amount',
    'due_date',
    'days_overdue',
    'status',
  ];

  constructor(
    private paymentTermsApi: PaymentTermsApiService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadReport();
  }

  loadReport() {
    this.isLoading = true;
    this.paymentTermsApi.getAgingReport().subscribe({
      next: (report: AgingReport) => {
        this.buckets = [
          {
            key: 'current',
            label: 'Aktuale (pa vonese)',
            entries: report.buckets.current,
            summary: report.summary.current,
          },
          {
            key: '1_30',
            label: '1-30 dite',
            entries: report.buckets['1_30'],
            summary: report.summary['1_30'],
          },
          {
            key: '31_60',
            label: '31-60 dite',
            entries: report.buckets['31_60'],
            summary: report.summary['31_60'],
          },
          {
            key: '61_90',
            label: '61-90 dite',
            entries: report.buckets['61_90'],
            summary: report.summary['61_90'],
          },
          {
            key: 'over_90',
            label: '90+ dite',
            entries: report.buckets.over_90,
            summary: report.summary.over_90,
          },
        ];
        this.grandTotal = this.buckets.reduce(
          (sum, b) => sum + b.summary.total,
          0
        );
        this.grandCount = this.buckets.reduce(
          (sum, b) => sum + b.summary.count,
          0
        );
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      },
    });
  }

  navigateToSale(id: number) {
    this.router.navigate(['/sale', id]);
  }

  getSeverityClass(key: string): string {
    const map: Record<string, string> = {
      current: 'severity-ok',
      '1_30': 'severity-low',
      '31_60': 'severity-medium',
      '61_90': 'severity-high',
      over_90: 'severity-critical',
    };
    return map[key] || '';
  }
}
