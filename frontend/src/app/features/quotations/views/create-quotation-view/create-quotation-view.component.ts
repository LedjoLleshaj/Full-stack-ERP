import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { QuotationApiService } from 'src/app/shared/services/quotation-api/quotation-api.service';
import { Product } from 'src/app/models/product.model';
import { Client } from 'src/app/models/client.model';
import { TaxRate } from 'src/app/models/tax-rate.model';
import { ProductService } from 'src/app/shared/services/product-api/product.service';
import { ClientService } from 'src/app/shared/services/clients-api/client.service';
import { TaxRateApiService } from 'src/app/shared/services/tax-rate-api/tax-rate-api.service';

@Component({
  selector: 'app-create-quotation-view',
  templateUrl: './create-quotation-view.component.html',
  styleUrls: ['./create-quotation-view.component.scss'],
})
export class CreateQuotationViewComponent implements OnInit {
  form!: FormGroup;
  clients: Client[] = [];
  products: Product[] = [];
  taxRates: any[] = [];
  currencies: string[] = ['EUR', 'USD', 'LEK'];
  isSubmitting = false;
  filteredClients: Client[] = [];
  clientSearchText = '';

  constructor(
    private fb: FormBuilder,
    private quotationService: QuotationApiService,
    private productService: ProductService,
    private clientService: ClientService,
    private taxRateService: TaxRateApiService,
    private router: Router,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.initForm();
    this.loadData();
  }

  private initForm(): void {
    const defaultValidUntil = new Date();
    defaultValidUntil.setDate(defaultValidUntil.getDate() + 30);

    this.form = this.fb.group({
      client: [null, Validators.required],
      currency: ['EUR', Validators.required],
      valid_until: [defaultValidUntil.toISOString().split('T')[0], Validators.required],
      notes: [''],
      items: this.fb.array([], Validators.required),
    });

    this.addItem();
  }

  private loadData(): void {
    this.productService.getProducts().subscribe((p) => (this.products = p));
    this.clientService.getClients().subscribe((c) => {
      this.clients = c;
      this.filteredClients = c;
    });
    this.taxRateService.getTaxRates().subscribe((t) => (this.taxRates = t));
  }

  get items(): FormArray {
    return this.form.get('items') as FormArray;
  }

  addItem(): void {
    this.items.push(
      this.fb.group({
        product: [null, Validators.required],
        quantity: [1, [Validators.required, Validators.min(1)]],
        unit_price: [0, [Validators.required, Validators.min(0.01)]],
        tax_rate: [null],
      })
    );
  }

  removeItem(index: number): void {
    if (this.items.length > 1) {
      this.items.removeAt(index);
    }
  }

  onProductChange(index: number): void {
    const item = this.items.at(index);
    const productId = item.get('product')?.value;
    const product = this.products.find((p) => p.id === productId);
    if (product) {
      item.get('unit_price')?.setValue(product.price);
    }
  }

  filterClients(event: Event): void {
    const value = (event.target as HTMLInputElement).value.toLowerCase();
    this.clientSearchText = value;
    this.filteredClients = this.clients.filter(
      (c) =>
        c.firstname.toLowerCase().includes(value) ||
        c.lastname.toLowerCase().includes(value) ||
        c.phone.includes(value)
    );
  }

  getClientDisplay(clientId: number): string {
    const client = this.clients.find((c) => c.id === clientId);
    return client ? `${client.firstname} ${client.lastname}` : '';
  }

  getItemSubtotal(index: number): number {
    const item = this.items.at(index);
    const qty = item.get('quantity')?.value || 0;
    const price = item.get('unit_price')?.value || 0;
    return qty * price;
  }

  getItemTax(index: number): number {
    const item = this.items.at(index);
    const taxRateId = item.get('tax_rate')?.value;
    if (!taxRateId) return 0;
    const rate = this.taxRates.find((t) => t.id === taxRateId);
    if (!rate) return 0;
    return (this.getItemSubtotal(index) * parseFloat(rate.rate)) / 100;
  }

  getItemTotal(index: number): number {
    return this.getItemSubtotal(index) + this.getItemTax(index);
  }

  getGrandTotal(): number {
    let total = 0;
    for (let i = 0; i < this.items.length; i++) {
      total += this.getItemTotal(i);
    }
    return total;
  }

  formatCurrency(amount: number): string {
    const currency = this.form.get('currency')?.value || 'EUR';
    const symbols: Record<string, string> = { EUR: '€', USD: '$', LEK: 'Lek' };
    return `${amount.toFixed(2)} ${symbols[currency] || currency}`;
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.snackBar.open('Plotëso të gjitha fushat e detyrueshme', 'Mbyll', { duration: 3000 });
      return;
    }

    this.isSubmitting = true;
    const formValue = this.form.value;

    const payload = {
      client: formValue.client,
      currency: formValue.currency,
      valid_until: formValue.valid_until,
      notes: formValue.notes,
      items: formValue.items.map((item: any) => ({
        product: item.product,
        quantity: item.quantity,
        unit_price: item.unit_price,
        tax_rate: item.tax_rate || null,
        tax_amount: 0,
      })),
    };

    this.quotationService.createQuotation(payload).subscribe({
      next: (result) => {
        this.snackBar.open('Oferta u krijua me sukses!', 'Mbyll', { duration: 3000 });
        this.router.navigate(['/quotations', result.id]);
      },
      error: (err) => {
        this.isSubmitting = false;
        const msg = err?.error?.error || 'Gabim në krijimin e ofertës';
        this.snackBar.open(msg, 'Mbyll', { duration: 5000 });
      },
    });
  }

  goBack(): void {
    this.router.navigate(['/quotations']);
  }
}
