import { Component, OnInit, OnDestroy } from "@angular/core";
import { EChartsOption } from "echarts";
import { Subscription } from "rxjs";
import { ReportsApiService, TopClient } from "src/app/shared/services/reports-api/reports-api.service";
import { DarkModeService } from "src/app/shared/services/dark-mode/dark-mode.service";

@Component({
  selector: "app-top-clients-view",
  templateUrl: "./top-clients-view.component.html",
  styleUrls: ["./top-clients-view.component.scss"],
})
export class TopClientsViewComponent implements OnInit, OnDestroy {
  chartOptions: EChartsOption = {};
  isLoading = true;
  isDarkMode = false;
  
  clients: TopClient[] = [];
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
      if (this.clients.length > 0) {
        this.initChart(this.clients);
      }
    });
    
    this.loadData();
  }

  ngOnDestroy() {
    this.darkModeSubscription?.unsubscribe();
  }

  private loadData() {
    this.reportsService.getTopClients().subscribe({
      next: (data: TopClient[]) => {
        this.clients = data;
        this.initChart(data);
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load top clients data:', err);
        this.isLoading = false;
      }
    });
  }

  private initChart(data: TopClient[]) {
    // Reverse for horizontal bar chart (top item at top)
    const chartData = [...data].reverse();
    
    const clientNames = chartData.map(c => c.name);
    const amounts = chartData.map(c => c.total_amount);

    // Vibrant gradient colors for bars
    const colors = [
      { start: '#10b981', end: '#34d399' }, // Emerald
      { start: '#0ea5e9', end: '#38bdf8' }, // Sky
      { start: '#8b5cf6', end: '#a78bfa' }, // Violet
      { start: '#f59e0b', end: '#fbbf24' }, // Amber
      { start: '#ec4899', end: '#f472b6' }, // Pink
    ];

    this.chartOptions = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        backgroundColor: this.isDarkMode ? '#1f2937' : '#fff',
        borderColor: this.isDarkMode ? '#374151' : '#e5e7eb',
        textStyle: {
          color: this.isDarkMode ? '#e5e7eb' : '#374151'
        },
        formatter: (params: any) => {
          const param = params[0];
          const client = data.find(c => c.name === param.name);
          const formatted = new Intl.NumberFormat('de-DE', {
            style: 'currency',
            currency: 'EUR'
          }).format(param.value);
          return `<strong>${param.name}</strong><br/>
                  Blerje totale: ${formatted}<br/>
                  Transaksione: ${client?.transaction_count || 0}`;
        }
      },
      grid: {
        left: '3%',
        right: '12%',
        bottom: '3%',
        top: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: this.isDarkMode ? '#4b5563' : '#d1d5db'
          }
        },
        axisLabel: {
          color: this.isDarkMode ? '#9ca3af' : '#6b7280',
          fontSize: 11,
          formatter: (value: number) => {
            if (value >= 1000) {
              return `€${(value / 1000).toFixed(0)}k`;
            }
            return `€${value}`;
          }
        },
        splitLine: {
          lineStyle: {
            color: this.isDarkMode ? '#374151' : '#e5e7eb'
          }
        }
      },
      yAxis: {
        type: 'category',
        data: clientNames,
        axisLine: {
          lineStyle: {
            color: this.isDarkMode ? '#4b5563' : '#d1d5db'
          }
        },
        axisLabel: {
          color: this.isDarkMode ? '#e5e7eb' : '#374151',
          fontSize: 13,
          fontWeight: 500
        }
      },
      series: [
        {
          name: 'Blerje totale',
          type: 'bar',
          barWidth: '60%',
          data: amounts.map((value, index) => ({
            value,
            itemStyle: {
              borderRadius: [0, 8, 8, 0],
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 1,
                y2: 0,
                colorStops: [
                  { offset: 0, color: colors[index % colors.length].start },
                  { offset: 1, color: colors[index % colors.length].end }
                ]
              }
            }
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          },
          label: {
            show: true,
            position: 'right',
            color: this.isDarkMode ? '#e5e7eb' : '#374151',
            fontSize: 12,
            fontWeight: 600,
            formatter: (params: any) => {
              return new Intl.NumberFormat('de-DE', {
                style: 'currency',
                currency: 'EUR',
                maximumFractionDigits: 0
              }).format(params.value);
            }
          }
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

  getTotalAmount(): number {
    return this.clients.reduce((sum, c) => sum + c.total_amount, 0);
  }

  getTotalTransactions(): number {
    return this.clients.reduce((sum, c) => sum + c.transaction_count, 0);
  }
}
