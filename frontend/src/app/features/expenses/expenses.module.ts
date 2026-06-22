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
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule } from '@angular/material/snack-bar';

import { ExpensesViewComponent } from './views/expenses-view/expenses-view.component';
import { AddExpenseViewComponent } from './views/add-expense-view/add-expense-view.component';

const routes: Routes = [
  { path: '', component: ExpensesViewComponent, title: 'Shpenzimet' },
  { path: 'add', component: AddExpenseViewComponent, title: 'Shto shpenzim' },
  { path: 'edit/:id', component: AddExpenseViewComponent, title: 'Modifiko shpenzimin' },
];

@NgModule({
  declarations: [ExpensesViewComponent, AddExpenseViewComponent],
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
    MatCheckboxModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
  ],
})
export class ExpensesModule {}
