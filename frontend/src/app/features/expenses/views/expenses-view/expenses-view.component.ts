import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { ExpenseApiService } from 'src/app/shared/services/expense-api/expense-api.service';
import { ExpenseCharge, RecurringExpense } from 'src/app/models/expense.model';
import { AuthApiService } from 'src/app/shared/services/auth-api/auth-api.service';

@Component({
  selector: 'app-expenses-view',
  templateUrl: './expenses-view.component.html',
  styleUrls: ['./expenses-view.component.scss'],
})
export class ExpensesViewComponent implements OnInit {
  displayedColumns = ['name', 'category', 'amount', 'frequency', 'next_due_date', 'auto', 'actions'];
  chargeColumns = ['expense_name', 'amount', 'period_date', 'charge_date', 'status'];
  expenses = new MatTableDataSource<RecurringExpense>();
  charges = new MatTableDataSource<ExpenseCharge>();
  isLoading = true;
  today = new Date().toISOString().slice(0, 10);

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private expenseService: ExpenseApiService,
    private router: Router,
    private snackBar: MatSnackBar,
    public authService: AuthApiService,
  ) {}

  ngOnInit(): void {
    this.load();
  }

  ngAfterViewInit(): void {
    this.expenses.paginator = this.paginator;
    this.expenses.sort = this.sort;
  }

  load(): void {
    this.isLoading = true;
    this.expenseService.list().subscribe({
      next: (data) => {
        this.expenses.data = data;
        this.isLoading = false;
      },
      error: () => {
        this.snackBar.open('Gabim në ngarkimin e shpenzimeve', 'Mbyll', { duration: 5000 });
        this.isLoading = false;
      },
    });
    this.expenseService.listCharges().subscribe({
      next: (data) => (this.charges.data = data),
      error: () =>
        this.snackBar.open('Gabim në ngarkimin e historikut', 'Mbyll', { duration: 5000 }),
    });
  }

  isDue(expense: RecurringExpense): boolean {
    return expense.next_due_date <= this.today;
  }

  addExpense(): void {
    this.router.navigate(['/expenses/add']);
  }

  editExpense(id: number): void {
    this.router.navigate(['/expenses/edit', id]);
  }

  chargeNow(expense: RecurringExpense): void {
    this.expenseService.charge(expense.id).subscribe({
      next: () => {
        this.snackBar.open(`U ngarkua: ${expense.name}`, 'Mbyll', { duration: 4000 });
        this.load();
      },
      error: (err) => {
        const msg = err?.error?.error || 'Ngarkimi dështoi';
        this.snackBar.open(msg, 'Mbyll', { duration: 5000 });
      },
    });
  }

  runDue(): void {
    this.expenseService.runDue().subscribe({
      next: (summary) => {
        this.snackBar.open(
          `U ngarkuan ${summary.charged} shpenzime (${summary.total_amount})`,
          'Mbyll',
          { duration: 5000 },
        );
        this.load();
      },
      error: () => this.snackBar.open('Procesi dështoi', 'Mbyll', { duration: 5000 }),
    });
  }

  deactivate(expense: RecurringExpense): void {
    this.expenseService.delete(expense.id).subscribe({
      next: () => {
        this.snackBar.open('Shpenzimi u çaktivizua', 'Mbyll', { duration: 4000 });
        this.load();
      },
      error: () => this.snackBar.open('Çaktivizimi dështoi', 'Mbyll', { duration: 5000 }),
    });
  }

  freqLabel(f: string): string {
    const labels: Record<string, string> = { DAILY: 'Ditore', WEEKLY: 'Javore', MONTHLY: 'Mujore' };
    return labels[f] || f;
  }

  formatCurrency(amount: string, currency: string): string {
    const symbols: Record<string, string> = { EUR: '€', USD: '$', LEK: 'Lek' };
    return `${Number(amount).toFixed(2)} ${symbols[currency] || currency}`;
  }
}
