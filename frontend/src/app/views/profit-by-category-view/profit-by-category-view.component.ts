import { Component, OnInit, OnDestroy } from "@angular/core";
import { EChartsOption } from "echarts";
import { Subscription } from "rxjs";
import { ReportsApiService, ProfitByCategory } from "src/app/shared/services/reports-api/reports-api.service";
import { DarkModeService } from "src/app/shared/services/dark-mode/dark-mode.service";

@Component({
  selector: "app-profit-by-category-view",
  templateUrl: "./profit-by-category-view.component.html",
  styleUrls: ["./profit-by-category-view.component.scss"],
})
export class ProfitByCategoryViewComponent implements OnInit, OnDestroy {
  chartOptions: EChartsOption = {};
  isLoading = true;
  isDarkMode = false;
  
  categories: ProfitByCategory[] = [];
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
      if (this.categories.length > 0) {
        this.initChart(this.categories);
      }
    });
    
    this.loadData();
  }

  ngOnDestroy() {
    this.darkModeSubscription?.unsubscribe();
  }

  private loadData() {
    this.reportsService.getProfitByCategory().subscribe({
      next: (data: ProfitByCategory[]) => {
        this.categories = data;
        this.initChart(data);
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load profit by category data:', err);
        this.isLoading = false;
      }
    });
  }

  private initChart(data: ProfitByCategory[]) {
    // Filter out categories with zero profit
    const chartData = data.filter(c => c.profit !== 0 || c.revenue > 0);

    // Vibrant colors for the donut chart
    const colors = [
      '#6366f1', // Indigo
      '#8b5cf6', // Violet
      '#ec4899', // Pink
      '#f97316', // Orange
      '#10b981', // Emerald
      '#0ea5e9', // Sky
      '#eab308', // Yellow
      '#ef4444', // Red
    ];

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
          const item = params.data;
          const formatCurrency = (val: number) => new Intl.NumberFormat('de-DE', {
            style: 'currency',
            currency: 'EUR'
          }).format(val);
          
          return `<strong>${params.name}</strong><br/>
                  Fitimi: ${formatCurrency(item.profit)}<br/>
                  Të ardhura: ${formatCurrency(item.revenue)}<br/>
                  Kosto: ${formatCurrency(item.cost)}<br/>
                  Përqindja: ${params.percent.toFixed(1)}%`;
        }
      },
      legend: {
        orient: 'horizontal',
        bottom: '5%',
        textStyle: {
          color: this.isDarkMode ? '#e5e7eb' : '#374151',
          fontSize: 12
        }
      },
      series: [
        {
          name: 'Fitimi sipas kategorisë',
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
            fontSize: 12,
            fontWeight: 500,
            formatter: (params: any) => {
              const value = params.data.profit as number;
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
              fontSize: 14,
              fontWeight: 'bold'
            }
          },
          data: chartData.map(c => ({
            value: Math.abs(c.profit), // Use absolute for sizing, color indicates +/-
            name: c.name,
            profit: c.profit,
            revenue: c.revenue,
            cost: c.cost,
            itemStyle: {
              color: c.profit < 0 ? '#ef4444' : undefined // Red for negative profit
            }
          })),
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

  getTotalProfit(): number {
    return this.categories.reduce((sum, c) => sum + c.profit, 0);
  }

  getTotalRevenue(): number {
    return this.categories.reduce((sum, c) => sum + c.revenue, 0);
  }

  getTotalCost(): number {
    return this.categories.reduce((sum, c) => sum + c.cost, 0);
  }
}
