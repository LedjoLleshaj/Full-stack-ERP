import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription, forkJoin } from 'rxjs';
import { EChartsOption } from 'echarts';
import { ProductService, ProductHistory, RecentSale, RecentRestock } from '../../../../shared/services/product-api/product.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { DarkModeService } from '../../../../shared/services/dark-mode/dark-mode.service';
import { CurrencyExchangeService } from '../../../../shared/services/currency-exchange/currency-exchange.service';

@Component({
  selector: 'app-product-details-view',
  templateUrl: './product-details-view.component.html',
  styleUrls: ['./product-details-view.component.scss']
})
export class ProductDetailsViewComponent implements OnInit, OnDestroy {
  productHistory: ProductHistory | null = null;
  isLoading = true;
  errorMessage = '';
  
  // Time period selection
  selectedMonths = 3;
  timePeriods = [
    { value: 1, label: '1 Muaj' },
    { value: 2, label: '2 Muaj' },
    { value: 3, label: '3 Muaj' },
    { value: 6, label: '6 Muaj' },
    { value: 12, label: '1 Vit' }
  ];
  
  // Chart
  chartOptions: EChartsOption = {};
  isDarkMode = false;
  
  // Exchange rates for currency conversion (to EUR)
  private exchangeRates: { [currency: string]: number } = { EUR: 1, USD: 0.85, LEK: 0.013 };
  
  // Tables
  salesColumns = ['date', 'client_name', 'quantity', 'price', 'status'];
  restocksColumns = ['date', 'supplier_name', 'quantity', 'price'];

  // Edit/Delete state
  isEditing = false;
  isSaving = false;
  isDeleting = false;
  editForm: { name?: string; category?: string; price?: number; description?: string } = {};

  private darkModeSubscription: Subscription | undefined;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private productService: ProductService,
    private darkModeService: DarkModeService,
    private currencyExchangeService: CurrencyExchangeService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.darkModeSubscription = this.darkModeService.darkMode$.subscribe(isDark => {
      this.isDarkMode = isDark;
      if (this.productHistory) {
        this.initChart();
      }
    });
    
    // Load exchange rates first, then load product history
    this.currencyExchangeService.getExchangeRates().subscribe(data => {
      // Build a map of currency -> EUR rate
      if (data.rates) {
        this.exchangeRates = {};
        for (const currency of Object.keys(data.rates)) {
          this.exchangeRates[currency] = data.rates[currency]?.['EUR'] || 1;
        }
      }
      this.loadProductHistory();
    });
  }

  ngOnDestroy(): void {
    this.darkModeSubscription?.unsubscribe();
  }

  loadProductHistory(): void {
    const productId = this.route.snapshot.paramMap.get('id');
    if (!productId) {
      this.errorMessage = 'ID e produktit mungon';
      this.isLoading = false;
      return;
    }

    this.isLoading = true;
    this.productService.getProductHistory(+productId, this.selectedMonths).subscribe({
      next: (data) => {
        this.productHistory = data;
        this.initChart();
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load product history:', err);
        this.errorMessage = 'Gabim në ngarkimin e të dhënave';
        this.isLoading = false;
      }
    });
  }

  onTimePeriodChange(months: number): void {
    this.selectedMonths = months;
    this.loadProductHistory();
  }

  /**
   * Convert price to EUR using exchange rates
   */
  private convertToEur(price: number, currency: string): number {
    const rate = this.exchangeRates[currency.toUpperCase()] || 1;
    return price * rate;
  }

  private initChart(): void {
    if (!this.productHistory) return;

    const { sale_prices, restock_prices } = this.productHistory.price_history;
    
    // Merge all dates and sort
    const allDates = new Set<string>();
    sale_prices.forEach(p => allDates.add(p.date));
    restock_prices.forEach(p => allDates.add(p.date));
    const sortedDates = Array.from(allDates).sort();
    
    // Map prices by date, converting to EUR for consistent chart display
    const salePriceMap = new Map(sale_prices.map(p => [p.date, this.convertToEur(p.price, p.currency)]));
    const restockPriceMap = new Map(restock_prices.map(p => [p.date, this.convertToEur(p.price, p.currency)]));
    
    // Build data arrays (null for missing data points)
    const saleData = sortedDates.map(d => salePriceMap.get(d) ?? null);
    const restockData = sortedDates.map(d => restockPriceMap.get(d) ?? null);
    
    const axisLabelColor = this.isDarkMode ? '#e5e7eb' : '#374151';

    this.chartOptions = {
      backgroundColor: 'transparent',
      axisPointer: {
        link: [{ xAxisIndex: 'all' }],
        triggerOn: 'mousemove|click'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'line',
          snap: true,
          lineStyle: {
            color: this.isDarkMode ? '#6b7280' : '#9ca3af',
            width: 1,
            type: 'dashed'
          }
        },
        backgroundColor: this.isDarkMode ? '#1f2937' : '#fff',
        borderColor: this.isDarkMode ? '#374151' : '#e5e7eb',
        textStyle: {
          color: this.isDarkMode ? '#e5e7eb' : '#374151'
        },
        formatter: (params: any) => {
          let result = params[0]?.name || '';
          params.forEach((p: any) => {
            if (p.value != null) {
              result += `<br/>${p.marker} ${p.seriesName}: <strong>${p.value.toFixed(2)} €</strong>`;
            }
          });
          return result;
        }
      },
      legend: {
        data: ['Çmimi Shitjes', 'Çmimi Blerjes'],
        bottom: 0,
        textStyle: {
          color: axisLabelColor
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '7%',
        top: '5%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: sortedDates.map(d => this.formatDate(d)),
        axisLabel: {
          rotate: 45,
          fontSize: 11,
          color: axisLabelColor
        },
        axisLine: {
          lineStyle: {
            color: this.isDarkMode ? '#4b5563' : '#d1d5db'
          }
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          fontSize: 12,
          color: axisLabelColor,
          formatter: (value: number) => `${value} €`
        },
        axisLine: {
          lineStyle: {
            color: this.isDarkMode ? '#4b5563' : '#d1d5db'
          }
        },
        splitLine: {
          lineStyle: {
            color: this.isDarkMode ? '#374151' : '#e5e7eb'
          }
        }
      },
      series: [
        {
          name: 'Çmimi Shitjes',
          type: 'line',
          data: saleData,
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            color: '#3b82f6',
            width: 1
          },
          itemStyle: {
            color: '#3b82f6'
          },
          connectNulls: true
        },
        {
          name: 'Çmimi Blerjes',
          type: 'line',
          data: restockData,
          smooth: true,
          symbol: 'diamond',
          symbolSize: 8,
          lineStyle: {
            color: '#f97316',
            width: 1
          },
          itemStyle: {
            color: '#f97316'
          },
          connectNulls: true
        }
      ]
    };
  }

  formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('sq-AL', { day: '2-digit', month: 'short' });
  }

  formatCurrency(amount: number, currency: string): string {
    const symbols: { [key: string]: string } = {
      'EUR': '€',
      'USD': '$',
      'LEK': 'Lek'
    };
    return `${amount.toFixed(2)} ${symbols[currency] || currency}`;
  }

  getStatusClass(status: string): string {
    const classes: { [key: string]: string } = {
      'COMPLETED': 'status-completed',
      'PARTIAL': 'status-partial',
      'PENDING': 'status-pending',
      'CANCELLED': 'status-cancelled'
    };
    return classes[status] || 'status-pending';
  }

  getStatusLabel(status: string): string {
    const labels: { [key: string]: string } = {
      'COMPLETED': 'Paguar',
      'PARTIAL': 'Pjesërisht',
      'PENDING': 'Pa Paguar',
      'CANCELLED': 'Anuluar'
    };
    return labels[status] || status;
  }

  goToSale(sale: RecentSale): void {
    if (sale.id) {
      this.router.navigate(['/sale', sale.id]);
    }
  }

  goBack(): void {
    this.router.navigate(['/products']);
  }

  getStockClass(): string {
    if (!this.productHistory) return '';
    const stock = this.productHistory.product.disponibility;
    if (stock <= 0) return 'stock-out';
    if (stock <= 10) return 'stock-low';
    return 'stock-ok';
  }

  // ========= EDIT/DELETE METHODS =========
  toggleEdit(): void {
    this.isEditing = !this.isEditing;
    if (this.isEditing && this.productHistory) {
      this.editForm = {
        name: this.productHistory.product.name,
        category: this.productHistory.product.category,
        price: this.productHistory.product.price,
        description: this.productHistory.product.description
      };
    }
  }

  saveEdit(): void {
    if (!this.productHistory?.product.id) return;

    this.isSaving = true;
    this.productService.updateProduct(this.productHistory.product.id, this.editForm).subscribe({
      next: (result) => {
        this.productHistory!.product = result;
        this.isEditing = false;
        this.isSaving = false;
        this.snackBar.open('Produkti u përditësua me sukses', 'Mbyll', { duration: 3000 });
      },
      error: (err) => {
        console.error('Failed to update product:', err);
        this.isSaving = false;
        this.snackBar.open('Gabim në përditësimin e produktit', 'Mbyll', { duration: 3000 });
      }
    });
  }

  confirmDelete(): void {
    // Check for inventory
    const stock = this.productHistory?.product.disponibility || 0;
    let message = `Jeni të sigurt që dëshironi të fshini produktin "${this.productHistory?.product.name}"?`;
    
    if (stock > 0) {
      message += `\n\n⚠️ KUJDES: Produkti ka ${stock} kg në stok!`;
    }
    
    message += '\n\nKy veprim është i pakthyeshëm.';

    if (window.confirm(message)) {
      this.deleteProduct();
    }
  }

  private deleteProduct(): void {
    if (!this.productHistory?.product.id) return;

    this.isDeleting = true;
    this.productService.deleteProduct(this.productHistory.product.id).subscribe({
      next: () => {
        this.snackBar.open('Produkti u fshi me sukses', 'Mbyll', { duration: 3000 });
        this.router.navigate(['/products']);
      },
      error: (err) => {
        console.error('Failed to delete product:', err);
        this.isDeleting = false;
        const errorMsg = err.error?.error || 'Gabim në fshirjen e produktit';
        this.snackBar.open(errorMsg, 'Mbyll', { duration: 5000 });
      }
    });
  }
}
