import { Component, OnInit, OnDestroy } from "@angular/core";
import { EChartsOption } from "echarts";
import { Subscription } from "rxjs";
import { ReportsApiService, PaidVsUnpaidStats } from "src/app/shared/services/reports-api/reports-api.service";
import { DarkModeService } from "src/app/shared/services/dark-mode/dark-mode.service";

@Component({
  selector: "app-paid-vs-unpaid-view",
  templateUrl: "./paid-vs-unpaid-view.component.html",
  styleUrls: ["./paid-vs-unpaid-view.component.scss"],
})
export class PaidVsUnpaidViewComponent implements OnInit, OnDestroy {
  chartOptions: EChartsOption = {};
  isLoading = true;
  isDarkMode = false;
  
  stats: PaidVsUnpaidStats | null = null;
  private darkModeSubscription: Subscription | undefined;

  constructor(
    private reportsService: ReportsApiService,
    private darkModeService: DarkModeService
  ) {}

  ngOnInit() {
    // Subscribe to dark mode changes
    this.darkModeSubscription = this.darkModeService.darkMode$.subscribe(isDark => {
      this.isDarkMode = isDark;
      // Re-render chart if data is already loaded
      if (this.stats) {
        this.initChart(this.stats);
      }
    });
    
    this.loadData();
  }

  ngOnDestroy() {
    this.darkModeSubscription?.unsubscribe();
  }

  private loadData() {
    this.reportsService.getPaidVsUnpaid().subscribe({
      next: (data: PaidVsUnpaidStats) => {
        this.stats = data;
        this.initChart(data);
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load paid vs unpaid data:', err);
        this.isLoading = false;
      }
    });
  }

  private initChart(data: PaidVsUnpaidStats) {
    const chartData = [
      { value: data.paid.amount, name: data.paid.label, count: data.paid.count },
      { value: data.partial.amount, name: data.partial.label, count: data.partial.count },
      { value: data.unpaid.amount, name: data.unpaid.label, count: data.unpaid.count },
    ].filter(item => item.value > 0); // Only show categories with values

    const colors = ['#22c55e', '#f59e0b', '#ef4444']; // Green, Amber, Red

    this.chartOptions = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: this.isDarkMode ? '#1f2937' : '#fff',
        borderColor: this.isDarkMode ? '#374151' : '#e5e7eb',
        textStyle: {
          color: this.isDarkMode ? '#e5e7eb' : '#374151'
        },
        formatter: (params: any) => {
          const value = params.value as number;
          const formatted = new Intl.NumberFormat('de-DE', {
            style: 'currency',
            currency: 'EUR'
          }).format(value);
          return `<strong>${params.name}</strong><br/>
                  Shuma: ${formatted}<br/>
                  Transaksione: ${params.data.count}<br/>
                  Përqindja: ${params.percent.toFixed(1)}%`;
        }
      },
      legend: {
        orient: 'horizontal',
        bottom: '5%',
        textStyle: {
          color: this.isDarkMode ? '#e5e7eb' : '#374151',
          fontSize: 14
        }
      },
      series: [
        {
          name: 'Paguar vs Pa Paguar',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 10,
            borderColor: this.isDarkMode ? '#1f2937' : '#fff',
            borderWidth: 3
          },
          label: {
            show: true,
            position: 'outside',
            color: this.isDarkMode ? '#e5e7eb' : '#374151',
            fontSize: 13,
            fontWeight: 500,
            formatter: (params: any) => {
              const value = params.value as number;
              const formatted = new Intl.NumberFormat('de-DE', {
                style: 'currency',
                currency: 'EUR',
                maximumFractionDigits: 0
              }).format(value);
              return `${params.name}\n${formatted}`;
            }
          },
          labelLine: {
            show: true,
            lineStyle: {
              color: this.isDarkMode ? '#6b7280' : '#9ca3af'
            }
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 20,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            },
            label: {
              fontSize: 16,
              fontWeight: 'bold'
            }
          },
          data: chartData,
          color: colors
        }
      ]
    };
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(value);
  }
}
