import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

// Standalone components from shared
import { SalesTableComponent } from '../../shared/components/sales-table/sales-table.component';
import { RestocksTableComponent } from '../../shared/components/restocks-table/restocks-table.component';

// Feature components
import { SalesViewComponent } from './views/sales-view/sales-view.component';
import { AddSaleViewComponent } from './views/add-sale-view/add-sale-view.component';
import { SaleDetailsViewComponent } from './views/sale-details-view/sale-details-view.component';
import { ReturnDialogComponent } from '../../shared/components/return-dialog/return-dialog.component';

// Material modules needed
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatRadioModule } from '@angular/material/radio';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDialogModule } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

// Shared pipes
import { PaymentStatusPipe, AlbanianCurrencyPipe, AlbanianDatePipe } from '../../shared/pipes';

const routes: Routes = [
  { path: '', component: SalesViewComponent, title: 'Sale History' },
  { path: 'add', component: AddSaleViewComponent, title: 'Add Sale' },
  { path: ':id', component: SaleDetailsViewComponent, title: 'Sale Details' },
];

@NgModule({
  declarations: [
    SalesViewComponent,
    AddSaleViewComponent,
    SaleDetailsViewComponent,
    ReturnDialogComponent,
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
    MatSelectModule,
    MatAutocompleteModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatProgressSpinnerModule,
    MatCardModule,
    MatChipsModule,
    MatRadioModule,
    MatCheckboxModule,
    MatDividerModule,
    MatProgressBarModule,
    MatDialogModule,
    MatTooltipModule,
    // Standalone components
    SalesTableComponent,
    // Pipes
    PaymentStatusPipe,
    AlbanianCurrencyPipe,
    AlbanianDatePipe,
  ],
})
export class SalesModule {}
