import { Component, OnInit, OnDestroy } from "@angular/core";
import { EChartsOption } from "echarts";
import { Subscription } from "rxjs";
import { ReportsApiService, DailyProfit } from "src/app/shared/services/reports-api/reports-api.service";
import { DarkModeService } from "src/app/shared/services/dark-mode/dark-mode.service";

interface PeriodOption {
  label: string;
  days: number;
}

@Component({
  selector: "app-revenue-view",
  templateUrl: "./revenue-view.component.html",
  styleUrls: ["./revenue-view.component.scss"],
})
export class RevenueViewComponent implements OnInit, OnDestroy {
  chartOptions: EChartsOption = {};
  isLoading = true;
  isDarkMode = false;
  
  // Period selection
  periodOptions: PeriodOption[] = [
    { label: '7 ditë', days: 7 },
    { label: '30 ditë', days: 30 },
    { label: '3 muaj', days: 90 },
    { label: '6 muaj', days: 180 },
    { label: '1 vit', days: 365 },
    { label: 'Të gjitha', days: 0 }
  ];
  selectedPeriod: PeriodOption = this.periodOptions[1]; // Default 30 days
  
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

  onPeriodChange(period: PeriodOption) {
    this.selectedPeriod = period;
    this.loadProfitData();
  }

  private loadProfitData() {
    this.isLoading = true;
    this.reportsService.getDailyProfit(this.selectedPeriod.days).subscribe({
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
    const originalDates = data.map(d => d.date); // Keep original dates for tooltip
    const salesData = data.map(d => d.sales);
    const purchasesData = data.map(d => -d.purchases); // Negative for display below zero line

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
          // Get full date with year from original data using dataIndex
          const dataIndex = params[0].dataIndex;
          const fullDate = this.formatDateWithYear(originalDates[dataIndex]);

          let tooltipHtml = `<strong>${fullDate}</strong><br/>`;
          
          params.forEach((param: any) => {
            const value = Math.abs(param.value as number);
            const formatted = new Intl.NumberFormat('de-DE', {
              style: 'currency',
              currency: 'EUR'
            }).format(value);
            const colorDot = `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${param.color};margin-right:5px;"></span>`;
            tooltipHtml += `${colorDot}${param.seriesName}: <strong>${formatted}</strong><br/>`;
          });
          
          // Calculate and show net profit
          const salesVal = params.find((p: any) => p.seriesName === 'Shitje')?.value || 0;
          const purchasesVal = params.find((p: any) => p.seriesName === 'Blerje')?.value || 0;
          const netProfit = salesVal + purchasesVal; // purchasesVal is already negative
          const netFormatted = new Intl.NumberFormat('de-DE', {
            style: 'currency',
            currency: 'EUR'
          }).format(netProfit);
          const netColor = netProfit >= 0 ? '#22c55e' : '#ef4444';
          tooltipHtml += `<hr style="margin:4px 0;border-color:${this.isDarkMode ? '#374151' : '#e5e7eb'}"/>`;
          tooltipHtml += `Fitimi Neto: <strong style="color:${netColor}">${netFormatted}</strong>`;
          
          return tooltipHtml;
        }
      },
      legend: {
        data: ['Shitje', 'Blerje'],
        textStyle: {
          color: axisLabelColor
        },
        top: 10
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '50px',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          rotate: 45,
          fontSize: 12,
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
          fontSize: 12,
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
          name: 'Shitje',
          type: 'bar',
          stack: 'total',
          itemStyle: {
            color: '#22c55e'
          },
          data: salesData.map(value => ({
            value,
            itemStyle: {
              color: '#22c55e',
              borderRadius: value > 0 ? [4, 4, 0, 0] : [0, 0, 4, 4]
            }
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          }
        },
        {
          name: 'Blerje',
          type: 'bar',
          stack: 'total',
          itemStyle: {
            color: '#ef4444'
          },
          data: purchasesData.map(value => ({
            value,
            itemStyle: {
              color: '#ef4444',
              borderRadius: value < 0 ? [0, 0, 4, 4] : [4, 4, 0, 0]
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

  private formatDateWithYear(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('sq-AL', { day: '2-digit', month: 'short', year: 'numeric' });
  }
}
