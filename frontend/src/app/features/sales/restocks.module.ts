import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

import { RestocksViewComponent } from './views/restocks-view/restocks-view.component';
import { RestockDetailsViewComponent } from './views/restock-details-view/restock-details-view.component';

// Standalone components
import { RestocksTableComponent } from '../../shared/components/restocks-table/restocks-table.component';

// Material
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

// Pipes
import { PaymentStatusPipe, AlbanianCurrencyPipe, AlbanianDatePipe } from '../../shared/pipes';

const routes: Routes = [
  { path: '', component: RestocksViewComponent, title: 'Restock History' },
  { path: ':id', component: RestockDetailsViewComponent, title: 'Restock Details' },
];

@NgModule({
  declarations: [
    RestocksViewComponent,
    RestockDetailsViewComponent,
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    RouterModule.forChild(routes),
    // Material
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatCardModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatDividerModule,
    MatProgressBarModule,
    MatChipsModule,
    // Standalone
    RestocksTableComponent,
    // Pipes
    PaymentStatusPipe,
    AlbanianCurrencyPipe,
    AlbanianDatePipe,
  ],
})
export class RestocksModule {}
