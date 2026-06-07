import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

// Feature components
import { ProductsViewComponent } from './views/products-view/products-view.component';
import { AddProductViewComponent } from './views/add-product-view/add-product-view.component';
import { ProductDetailsViewComponent } from './views/product-details-view/product-details-view.component';

// Standalone components
import { ProductTableComponent } from '../../shared/components/product-table/product-table.component';
import { ChipsComponent } from '../../shared/components/chips/chips.component';

// Material
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
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatRadioModule } from '@angular/material/radio';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';

// Dialogs
import { EditPriceDialogComponent } from '../../dialogs/edit-price-dialog/edit-price-dialog.component';

// Pipes
import { AlbanianCurrencyPipe, AlbanianDatePipe, PaymentStatusPipe } from '../../shared/pipes';

// Charts
import { NgxEchartsModule } from 'ngx-echarts';

const routes: Routes = [
  { path: '', component: ProductsViewComponent, title: 'Products' },
  { path: 'add', component: AddProductViewComponent, title: 'Add Product' },
  { path: ':id', component: ProductDetailsViewComponent, title: 'Product Details' },
];

@NgModule({
  declarations: [
    ProductsViewComponent,
    AddProductViewComponent,
    ProductDetailsViewComponent,
    EditPriceDialogComponent,
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    RouterModule.forChild(routes),
    NgxEchartsModule,
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
    MatCardModule,
    MatProgressSpinnerModule,
    MatRadioModule,
    MatCheckboxModule,
    MatDialogModule,
    MatButtonToggleModule,
    MatDividerModule,
    MatTooltipModule,
    // Standalone
    ProductTableComponent,
    ChipsComponent,
    // Pipes
    AlbanianCurrencyPipe,
    AlbanianDatePipe,
    PaymentStatusPipe,
  ],
})
export class ProductsModule {}
