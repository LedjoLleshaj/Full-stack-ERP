/**
 * SharedModule - Contains reusable components, pipes, and common module exports.
 * Import this module in any feature module that needs these shared resources.
 */
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// Material Modules (commonly used across features)
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

// Shared Pipes (standalone)
import { PaymentStatusPipe, AlbanianCurrencyPipe, AlbanianDatePipe } from './pipes';

// Shared Components (standalone)
import { ChipsComponent } from './components/chips/chips.component';
import { SalesTableComponent } from './components/sales-table/sales-table.component';
import { RestocksTableComponent } from './components/restocks-table/restocks-table.component';

const MATERIAL_MODULES = [
  MatTableModule,
  MatSortModule,
  MatPaginatorModule,
  MatButtonModule,
  MatIconModule,
  MatFormFieldModule,
  MatInputModule,
  MatSelectModule,
  MatAutocompleteModule,
  MatChipsModule,
  MatDialogModule,
  MatSnackBarModule,
  MatTooltipModule,
  MatProgressSpinnerModule,
];

const STANDALONE_COMPONENTS = [
  ChipsComponent,
  SalesTableComponent,
  RestocksTableComponent,
];

const STANDALONE_PIPES = [
  PaymentStatusPipe,
  AlbanianCurrencyPipe,
  AlbanianDatePipe,
];

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    ...MATERIAL_MODULES,
    ...STANDALONE_COMPONENTS,
    ...STANDALONE_PIPES,
  ],
  exports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    ...MATERIAL_MODULES,
    ...STANDALONE_COMPONENTS,
    ...STANDALONE_PIPES,
  ],
})
export class SharedModule {}
