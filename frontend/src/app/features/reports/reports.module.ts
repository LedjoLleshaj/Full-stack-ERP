import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

// Feature components
import { ReportsViewComponent } from './views/reports-view/reports-view.component';
import { RevenueViewComponent } from './views/revenue-view/revenue-view.component';
import { PaidVsUnpaidViewComponent } from './views/paid-vs-unpaid-view/paid-vs-unpaid-view.component';
import { TopProductsViewComponent } from './views/top-products-view/top-products-view.component';
import { ProfitByCategoryViewComponent } from './views/profit-by-category-view/profit-by-category-view.component';
import { TopClientsViewComponent } from './views/top-clients-view/top-clients-view.component';
import { AlertsViewComponent } from './views/alerts-view/alerts-view.component';

// Material
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

// Charts
import { NgxEchartsModule } from 'ngx-echarts';

// Pipes
import { AlbanianCurrencyPipe } from '../../shared/pipes';

const routes: Routes = [
  { path: '', component: ReportsViewComponent, title: 'Reports - Selita' },
  { path: 'revenue', component: RevenueViewComponent, title: 'Revenue Trend - Selita' },
  { path: 'paid-vs-unpaid', component: PaidVsUnpaidViewComponent, title: 'Paid vs Unpaid - Selita' },
  { path: 'top-products', component: TopProductsViewComponent, title: 'Top Products - Selita' },
  { path: 'profit-by-category', component: ProfitByCategoryViewComponent, title: 'Profit By Category - Selita' },
  { path: 'top-clients', component: TopClientsViewComponent, title: 'Top Clients - Selita' },
  { path: 'alerts', component: AlertsViewComponent, title: 'Alerts - Selita' },
];

@NgModule({
  declarations: [
    ReportsViewComponent,
    RevenueViewComponent,
    PaidVsUnpaidViewComponent,
    TopProductsViewComponent,
    ProfitByCategoryViewComponent,
    TopClientsViewComponent,
    AlertsViewComponent,
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    RouterModule.forChild(routes),
    NgxEchartsModule,
    // Material
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatTableModule,
    MatProgressSpinnerModule,
    MatDividerModule,
    MatFormFieldModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    // Pipes
    AlbanianCurrencyPipe,
  ],
})
export class ReportsModule {}
