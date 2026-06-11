import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCardModule } from '@angular/material/card';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';

import { QuotationsViewComponent } from './views/quotations-view/quotations-view.component';
import { CreateQuotationViewComponent } from './views/create-quotation-view/create-quotation-view.component';
import { QuotationDetailsViewComponent } from './views/quotation-details-view/quotation-details-view.component';

const routes: Routes = [
  { path: '', component: QuotationsViewComponent, title: 'Ofertat' },
  { path: 'create', component: CreateQuotationViewComponent, title: 'Ofertë e Re' },
  { path: ':id', component: QuotationDetailsViewComponent, title: 'Detajet e Ofertës' },
];

@NgModule({
  declarations: [
    QuotationsViewComponent,
    CreateQuotationViewComponent,
    QuotationDetailsViewComponent,
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    RouterModule.forChild(routes),
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    MatCardModule,
    MatTooltipModule,
    MatDialogModule,
    MatSnackBarModule,
  ],
})
export class QuotationsModule {}
