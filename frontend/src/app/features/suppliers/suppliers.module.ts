import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

// Feature components
import { SupplierViewComponent } from './views/suppliers-view/supplier-view.component';
import { AddSupplierViewComponent } from './views/add-supplier-view/add-supplier-view.component';
import { SupplierDetailsViewComponent } from './views/supplier-details-view/supplier-details-view.component';

// Standalone components
import { SupplierTableComponent } from '../../shared/components/supplier-table/supplier-table.component';
import { RestocksTableComponent } from '../../shared/components/restocks-table/restocks-table.component';

// Material
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';

// Pipes
import { PaymentStatusPipe, AlbanianCurrencyPipe, AlbanianDatePipe } from '../../shared/pipes';

const routes: Routes = [
  { path: '', component: SupplierViewComponent, title: 'Supplier List - Selita' },
  { path: 'add', component: AddSupplierViewComponent, title: 'Add Supplier - Selita' },
  { path: ':id', component: SupplierDetailsViewComponent, title: 'Supplier Details - Selita' },
];

@NgModule({
  declarations: [
    SupplierViewComponent,
    AddSupplierViewComponent,
    SupplierDetailsViewComponent,
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
    MatCardModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatDividerModule,
    // Standalone
    SupplierTableComponent,
    RestocksTableComponent,
    // Pipes
    PaymentStatusPipe,
    AlbanianCurrencyPipe,
    AlbanianDatePipe,
  ],
})
export class SuppliersModule {}
