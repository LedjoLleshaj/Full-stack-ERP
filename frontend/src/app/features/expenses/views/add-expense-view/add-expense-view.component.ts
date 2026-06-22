import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ExpenseApiService } from 'src/app/shared/services/expense-api/expense-api.service';

@Component({
  selector: 'app-add-expense-view',
  templateUrl: './add-expense-view.component.html',
  styleUrls: ['./add-expense-view.component.scss'],
})
export class AddExpenseViewComponent implements OnInit {
  form!: FormGroup;
  editId: number | null = null;
  currencies = ['EUR', 'USD', 'LEK'];
  accountTypes = ['CASH', 'BANK'];
  frequencies = [
    { value: 'DAILY', label: 'Ditore' },
    { value: 'WEEKLY', label: 'Javore' },
    { value: 'MONTHLY', label: 'Mujore' },
  ];

  constructor(
    private fb: FormBuilder,
    private expenseService: ExpenseApiService,
    private router: Router,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      name: ['', Validators.required],
      category: [''],
      description: [''],
      amount: [null, [Validators.required, Validators.min(0.01)]],
      currency: ['EUR', Validators.required],
      account_type: ['BANK', Validators.required],
      frequency: ['MONTHLY', Validators.required],
      start_date: [null, Validators.required],
      end_date: [null],
      auto_charge: [true],
    });

    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.editId = Number(id);
      this.expenseService.get(this.editId).subscribe({
        next: (e) => this.form.patchValue(e),
        error: () => {
          this.snackBar.open('Shpenzimi nuk u gjet', 'Mbyll', { duration: 5000 });
          this.router.navigate(['/expenses']);
        },
      });
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const payload = this.form.value;
    const req$ = this.editId
      ? this.expenseService.update(this.editId, payload)
      : this.expenseService.create(payload);
    req$.subscribe({
      next: () => {
        this.snackBar.open('Shpenzimi u ruajt', 'Mbyll', { duration: 4000 });
        this.router.navigate(['/expenses']);
      },
      error: (err) => {
        const msg = err?.error?.message?.account_type?.[0] || 'Ruajtja dështoi';
        this.snackBar.open(msg, 'Mbyll', { duration: 5000 });
      },
    });
  }

  cancel(): void {
    this.router.navigate(['/expenses']);
  }
}
