import { Component, OnInit, OnDestroy } from "@angular/core";
import { EChartsOption } from "echarts";
import { Subscription } from "rxjs";
import { ReportsApiService, DailyProfit } from "src/app/shared/services/reports-api/reports-api.service";
import { DarkModeService } from "src/app/shared/services/dark-mode/dark-mode.service";

@Component({
  selector: "app-revenue-view",
  templateUrl: "./revenue-view.component.html",
  styleUrls: ["./revenue-view.component.scss"],
})
export class RevenueViewComponent implements OnInit, OnDestroy {
  chartOptions: EChartsOption = {};
  isLoading = true;
  isDarkMode = false;
  
  private profitData: DailyProfit[] = [];
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
      if (this.profitData.length > 0) {
        this.initChart(this.profitData);
      }
    });
    
    this.loadProfitData();
  }

  ngOnDestroy() {
    this.darkModeSubscription?.unsubscribe();
  }

  private loadProfitData() {
    this.reportsService.getDailyProfit().subscribe({
      next: (data: DailyProfit[]) => {
        this.profitData = data;
        this.initChart(data);
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load profit data:', err);
        this.isLoading = false;
      }
    });
  }

  private initChart(data: DailyProfit[]) {
    const dates = data.map(d => this.formatDate(d.date));
    const profits = data.map(d => d.profit);

    // Calculate colors - green for positive, red for negative
    const barColors = profits.map(p => p >= 0 ? '#22c55e' : '#ef4444');

    // Use dark mode from service
    const axisLabelColor = this.isDarkMode ? '#e5e7eb' : '#374151';

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
          const value = param.value as number;
          const formatted = new Intl.NumberFormat('de-DE', {
            style: 'currency',
            currency: 'EUR'
          }).format(value);
          return `${param.name}<br/>Fitimi: <strong>${formatted}</strong>`;
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          rotate: 45,
          fontSize: 13,
          color: axisLabelColor,
          fontWeight: 500
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
          fontSize: 13,
          color: axisLabelColor,
          fontWeight: 500,
          formatter: (value: number) => {
            if (Math.abs(value) >= 1000) {
              return (value / 1000).toFixed(1) + 'k €';
            }
            return value + ' €';
          }
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
          name: 'Fitimi',
          type: 'bar',
          data: profits.map((value, index) => ({
            value,
            itemStyle: {
              color: barColors[index],
              borderRadius: [4, 4, 0, 0]
            }
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          }
        }
      ]
    };
  }

  private formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('sq-AL', { day: '2-digit', month: 'short' });
  }
}
