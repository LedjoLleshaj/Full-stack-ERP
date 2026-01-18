import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

// Feature components
import { ClientViewComponent } from '../../views/clients-view/client-view.component';
import { AddClientViewComponent } from '../../views/add-client-view/add-client-view.component';
import { ClientDetailsViewComponent } from '../../views/client-details-view/client-details-view.component';

// Standalone components
import { ClientTableComponent } from '../../shared/components/client-table/client-table.component';
import { SalesTableComponent } from '../../shared/components/sales-table/sales-table.component';

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
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';

// Pipes
import { PaymentStatusPipe, AlbanianCurrencyPipe, AlbanianDatePipe } from '../../shared/pipes';

const routes: Routes = [
  { path: '', component: ClientViewComponent, title: 'Client List - Selita' },
  { path: 'add', component: AddClientViewComponent, title: 'Add Client - Selita' },
  { path: ':id', component: ClientDetailsViewComponent, title: 'Client Details - Selita' },
];

@NgModule({
  declarations: [
    ClientViewComponent,
    AddClientViewComponent,
    ClientDetailsViewComponent,
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
    MatAutocompleteModule,
    MatSelectModule,
    MatRadioModule,
    // Standalone
    ClientTableComponent,
    SalesTableComponent,
    // Pipes
    PaymentStatusPipe,
    AlbanianCurrencyPipe,
    AlbanianDatePipe,
  ],
})
export class ClientsModule {}
