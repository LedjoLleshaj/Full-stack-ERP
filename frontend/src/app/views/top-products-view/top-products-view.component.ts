import { Component, OnInit, OnDestroy } from "@angular/core";
import { EChartsOption } from "echarts";
import { Subscription } from "rxjs";
import { ReportsApiService, TopProduct } from "src/app/shared/services/reports-api/reports-api.service";
import { DarkModeService } from "src/app/shared/services/dark-mode/dark-mode.service";

@Component({
  selector: "app-top-products-view",
  templateUrl: "./top-products-view.component.html",
  styleUrls: ["./top-products-view.component.scss"],
})
export class TopProductsViewComponent implements OnInit, OnDestroy {
  chartOptions: EChartsOption = {};
  isLoading = true;
  isDarkMode = false;
  
  products: TopProduct[] = [];
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
      if (this.products.length > 0) {
        this.initChart(this.products);
      }
    });
    
    this.loadData();
  }

  ngOnDestroy() {
    this.darkModeSubscription?.unsubscribe();
  }

  private loadData() {
    this.reportsService.getTopProducts().subscribe({
      next: (data: TopProduct[]) => {
        this.products = data;
        this.initChart(data);
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load top products data:', err);
        this.isLoading = false;
      }
    });
  }

  private initChart(data: TopProduct[]) {
    // Reverse for horizontal bar chart (top item at top)
    const chartData = [...data].reverse();
    
    const productNames = chartData.map(p => p.name);
    const quantities = chartData.map(p => p.quantity);

    // Vibrant gradient colors for bars
    const colors = [
      { start: '#6366f1', end: '#818cf8' }, // Indigo
      { start: '#8b5cf6', end: '#a78bfa' }, // Violet
      { start: '#ec4899', end: '#f472b6' }, // Pink
      { start: '#f97316', end: '#fb923c' }, // Orange
      { start: '#10b981', end: '#34d399' }, // Emerald
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
          return `<strong>${param.name}</strong><br/>Sasia e shitur: ${param.value.toLocaleString('de-DE')} kg`;
        }
      },
      grid: {
        left: '3%',
        right: '8%',
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
          fontSize: 12,
          formatter: (value: number) => value.toLocaleString('de-DE')
        },
        splitLine: {
          lineStyle: {
            color: this.isDarkMode ? '#374151' : '#e5e7eb'
          }
        }
      },
      yAxis: {
        type: 'category',
        data: productNames,
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
          name: 'Sasia e shitur',
          type: 'bar',
          barWidth: '60%',
          data: quantities.map((value, index) => ({
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
            formatter: (params: any) => `${params.value.toLocaleString('de-DE')} kg`
          }
        }
      ]
    };
  }
}
