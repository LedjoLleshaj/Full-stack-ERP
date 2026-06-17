import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { Observable, Subject } from 'rxjs';
import { take } from 'rxjs/operators';

import { Client } from 'src/app/models/client.model';
import { Product } from 'src/app/models/product.model';
import { PaymentTerms } from 'src/app/models/payment-terms.model';
import { TaxRate } from 'src/app/models/tax-rate.model';
import { ClientService } from '../clients-api/client.service';
import { ProductService } from '../product-api/product.service';
import { SalesApiService } from '../sales-api/sales-api.service';
import { CurrencyExchangeService } from '../currency-exchange/currency-exchange.service';
import { PaymentTermsApiService } from '../payment-terms-api/payment-terms-api.service';
import { TaxRateApiService } from '../tax-rate-api/tax-rate-api.service';
import {
  CreateSaleRequest,
  UpdateSaleRequest,
  SaleCreateResponse,
  SaleUpdateResponse,
  SaleDetails,
} from 'src/app/models/sale.model';

// ======== State interfaces ========

export interface SaleLineItemFormState {
  id?: number;
  selectedProduct: Product | null;
  productSearchText: string;
  quantity: number;
  price: number;
  basePriceEUR: number;
  taxRateId: number | null;
  discountType: string | null;
  discountValue: number;
  lastSoldPrice: number | null;
  lastSoldCurrency: string | null;
}

export interface SaleFormState {
  // Client selection
  availableClients: Client[];
  selectedClient: Client | null;
  clientSearchText: string;

  // Products
  availableProducts: Product[];

  // Line items (multi-product)
  items: SaleLineItemFormState[];

  // Payment options
  isPaid: boolean;
  paymentMethod: string;
  currency: string;

  // Tax rates
  availableTaxRates: TaxRate[];

  // Payment terms
  availablePaymentTerms: PaymentTerms[];
  selectedPaymentTermsId: number | null;

  // UI state
  isSubmitting: boolean;
}

// ======== Helpers ========

const createEmptyItem = (): SaleLineItemFormState => ({
  selectedProduct: null,
  productSearchText: '',
  quantity: 1,
  price: 0,
  basePriceEUR: 0,
  taxRateId: null,
  discountType: null,
  discountValue: 0,
  lastSoldPrice: null,
  lastSoldCurrency: null,
});

/**
 * Service to centralize multi-item sale creation logic.
 * Manages an items[] array instead of a single product.
 */
@Injectable({
  providedIn: 'root',
})
export class SaleFormService {
  // Constants
  readonly paymentMethods: string[] = ['CASH', 'CARD'];
  readonly currencies: string[] = ['EUR', 'USD', 'LEK'];

  // Internal state
  state: SaleFormState = this.getInitialState();

  // State change notification
  private stateChange$ = new Subject<void>();
  onStateChange = this.stateChange$.asObservable();

  constructor(
    private clientService: ClientService,
    private productService: ProductService,
    private salesApiService: SalesApiService,
    private currencyExchange: CurrencyExchangeService,
    private paymentTermsService: PaymentTermsApiService,
    private taxRateService: TaxRateApiService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  // ======== State initialisation ========

  getInitialState(): SaleFormState {
    return {
      availableClients: [],
      selectedClient: null,
      clientSearchText: '',
      availableProducts: [],
      items: [createEmptyItem()],
      isPaid: false,
      paymentMethod: 'CASH',
      currency: 'EUR',
      availableTaxRates: [],
      availablePaymentTerms: [],
      selectedPaymentTermsId: null,
      isSubmitting: false,
    };
  }

  resetForm(): void {
    this.state = this.getInitialState();
    this.stateChange$.next();
  }

  // ======== Item management ========

  addItem(): void {
    this.state.items = [...this.state.items, createEmptyItem()];
    this.stateChange$.next();
  }

  removeItem(index: number): void {
    if (this.state.items.length <= 1) return;
    this.state.items = this.state.items.filter((_, i) => i !== index);
    this.stateChange$.next();
  }

  onItemProductSelect(index: number, product: Product): void {
    if (!this.state.items[index]) return;

    // Convert price to current currency
    if (this.state.currency === 'EUR') {
      this.state.items = this.state.items.map((it, i) =>
        i === index
          ? { ...it, selectedProduct: product, productSearchText: product.name, basePriceEUR: product.price, price: product.price }
          : it
      );
      this.stateChange$.next();
    } else {
      this.currencyExchange.getExchangeRate('EUR', this.state.currency).pipe(take(1)).subscribe({
        next: (rate) => {
          this.state.items = this.state.items.map((it, i) =>
            i === index
              ? { ...it, selectedProduct: product, productSearchText: product.name, basePriceEUR: product.price, price: Math.round(product.price * rate * 100) / 100 }
              : it
          );
          this.stateChange$.next();
        },
        error: () => {
          this.state.items = this.state.items.map((it, i) =>
            i === index
              ? { ...it, selectedProduct: product, productSearchText: product.name, basePriceEUR: product.price, price: product.price }
              : it
          );
          this.snackBar.open('Gabim në marrjen e kursit të këmbimit', 'Mbyll', { duration: 3000 });
          this.stateChange$.next();
        },
      });
    }

    // Fetch last sold price if client is selected
    if (this.state.selectedClient?.id && product.id) {
      this.fetchLastSoldPrice(index);
    }
  }

  updateItemField(index: number, field: string, value: any): void {
    if (!this.state.items[index]) return;
    this.state.items = this.state.items.map((it, i) =>
      i === index ? { ...it, [field]: value } : it
    );
    this.stateChange$.next();
  }

  // ======== Currency handling ========

  onCurrencyChange(currency: string): void {
    this.state.currency = currency;

    if (currency === 'EUR') {
      // Reset all items to base EUR price
      this.state.items = this.state.items.map(item => ({
        ...item,
        price: item.basePriceEUR > 0 ? item.basePriceEUR : item.price,
      }));
      this.stateChange$.next();
    } else {
      this.currencyExchange.getExchangeRate('EUR', currency).pipe(take(1)).subscribe({
        next: (rate) => {
          this.state.items = this.state.items.map(item => ({
            ...item,
            price: item.basePriceEUR > 0
              ? Math.round(item.basePriceEUR * rate * 100) / 100
              : item.price,
          }));
          this.stateChange$.next();
        },
        error: () => {
          this.snackBar.open('Gabim në marrjen e kursit të këmbimit', 'Mbyll', { duration: 3000 });
        },
      });
    }
  }

  // ======== Client handling ========

  onClientSelect(client: Client): void {
    this.state.selectedClient = client;
    this.state.clientSearchText = `${client.firstname} ${client.lastname}`;
    // Clear last-sold prices immutably, then re-fetch for items that have a product
    this.state.items = this.state.items.map(item => ({
      ...item,
      lastSoldPrice: null,
      lastSoldCurrency: null,
    }));
    this.state.items.forEach((item, idx) => {
      if (item.selectedProduct?.id) {
        this.fetchLastSoldPrice(idx);
      }
    });
    this.stateChange$.next();
  }

  // ======== Last-sold price ========

  fetchLastSoldPrice(index: number): void {
    const item = this.state.items[index];
    if (!item || !this.state.selectedClient?.id || !item.selectedProduct?.id) return;

    this.salesApiService
      .getLastSoldPrice(this.state.selectedClient.id, item.selectedProduct.id)
      .pipe(take(1))
      .subscribe({
        next: (response) => {
          this.state.items = this.state.items.map((it, i) =>
            i === index
              ? { ...it, lastSoldPrice: response.price, lastSoldCurrency: response.currency }
              : it
          );
          this.stateChange$.next();
        },
        error: (err) => {
          console.error('Failed to fetch last sold price:', err);
          this.state.items = this.state.items.map((it, i) =>
            i === index ? { ...it, lastSoldPrice: null, lastSoldCurrency: null } : it
          );
        },
      });
  }

  // ======== Per-item calculations ========

  getItemSubtotal(index: number): number {
    const item = this.state.items[index];
    if (!item) return 0;
    return item.price * item.quantity;
  }

  getItemDiscountAmount(index: number): number {
    const item = this.state.items[index];
    if (!item || !item.discountType || item.discountValue <= 0) return 0;
    const subtotal = this.getItemSubtotal(index);
    if (item.discountType === 'PERCENT') {
      return Math.round(subtotal * item.discountValue / 100 * 100) / 100;
    }
    // FIXED
    return Math.min(item.discountValue, subtotal);
  }

  getItemTaxAmount(index: number): number {
    const item = this.state.items[index];
    if (!item || !item.taxRateId) return 0;
    const rate = this.state.availableTaxRates.find(r => r.id === item.taxRateId);
    if (!rate) return 0;
    const pct = parseFloat(String(rate.rate));
    if (!isFinite(pct) || pct < 0) return 0;
    const discountedSubtotal = this.getItemSubtotal(index) - this.getItemDiscountAmount(index);
    return Math.round(discountedSubtotal * pct / 100 * 100) / 100;
  }

  getItemLineTotal(index: number): number {
    return (
      this.getItemSubtotal(index) -
      this.getItemDiscountAmount(index) +
      this.getItemTaxAmount(index)
    );
  }

  // ======== Grand totals ========

  getGrandSubtotal(): number {
    return this.state.items.reduce((sum, _, i) => sum + this.getItemSubtotal(i), 0);
  }

  getGrandDiscount(): number {
    return this.state.items.reduce((sum, _, i) => sum + this.getItemDiscountAmount(i), 0);
  }

  getGrandTax(): number {
    return this.state.items.reduce((sum, _, i) => sum + this.getItemTaxAmount(i), 0);
  }

  getGrandTotal(): number {
    return this.state.items.reduce((sum, _, i) => sum + this.getItemLineTotal(i), 0);
  }

  // ======== Data loading ========

  loadClients(): void {
    this.clientService.getClients().pipe(take(1)).subscribe({
      next: (clients) => {
        this.state.availableClients = clients;
        this.stateChange$.next();
      },
      error: (err) => {
        console.error('Failed to fetch clients:', err);
        this.snackBar.open('Gabim ne ngarkimin e klienteve', 'Mbyll', { duration: 3000 });
      },
    });
  }

  loadProducts(): void {
    this.productService.getProducts().pipe(take(1)).subscribe({
      next: (products) => {
        this.state.availableProducts = products.filter(p => p.disponibility > 0);
        this.stateChange$.next();
      },
      error: (err) => {
        console.error('Failed to fetch products:', err);
        this.snackBar.open('Gabim ne ngarkimin e produkteve', 'Mbyll', { duration: 3000 });
      },
    });
  }

  loadTaxRates(): void {
    this.taxRateService.getTaxRates().pipe(take(1)).subscribe({
      next: (rates) => {
        this.state.availableTaxRates = rates;
        this.stateChange$.next();
      },
      error: (err) => {
        console.error('Failed to fetch tax rates:', err);
      },
    });
  }

  loadPaymentTerms(): void {
    this.paymentTermsService.getPaymentTerms().pipe(take(1)).subscribe({
      next: (terms) => {
        this.state.availablePaymentTerms = terms;
        this.stateChange$.next();
      },
      error: (err) => {
        console.error('Failed to fetch payment terms:', err);
      },
    });
  }

  // ======== Validation ========

  canCreateSale(): boolean {
    if (!this.state.selectedClient || this.state.items.length === 0 || this.state.isSubmitting) {
      return false;
    }
    return this.state.items.every(
      item => item.selectedProduct != null && item.price > 0 && item.quantity > 0
    );
  }

  // ======== Sale creation / update ========

  createSale(): Observable<SaleCreateResponse> {
    const req: CreateSaleRequest = {
      client_id: this.state.selectedClient!.id!,
      currency: this.state.currency,
      payment_terms_id: this.state.selectedPaymentTermsId || null,
      items: this.state.items.map(item => ({
        prod: item.selectedProduct!.id!,
        prod_price: item.price,
        quantity: item.quantity,
        tax_rate_id: item.taxRateId || null,
        discount_type: item.discountType || null,
        discount_value: item.discountValue || 0,
      })),
    };

    if (this.state.isPaid) {
      req.payment = {
        amount: this.getGrandTotal(),
        currency: this.state.currency,
        payment_method: this.state.paymentMethod as 'CASH' | 'CARD',
      };
    }

    return this.salesApiService.createSale(req);
  }

  updateSale(transactionId: number): Observable<SaleUpdateResponse> {
    const req: UpdateSaleRequest = {
      client_id: this.state.selectedClient!.id!,
      currency: this.state.currency,
      payment_terms_id: this.state.selectedPaymentTermsId || null,
      items: this.state.items.map(item => ({
        id: item.id,
        prod: item.selectedProduct!.id!,
        prod_price: item.price,
        quantity: item.quantity,
        tax_rate_id: item.taxRateId || null,
        discount_type: item.discountType || null,
        discount_value: item.discountValue || 0,
      })),
    };

    return this.salesApiService.updateSale(transactionId, req);
  }

  // ======== Edit loading ========

  loadForEdit(saleDetails: SaleDetails): void {
    const tx = saleDetails.transaction;

    // Set client (use ClientInfo from SaleDetails if available, map to Client shape)
    if (saleDetails.client) {
      const c = saleDetails.client;
      this.state.selectedClient = {
        id: c.id,
        firstname: c.firstname,
        lastname: c.lastname,
        email: '',
        phone: c.phone,
        address: c.address,
        city: c.city,
        unpaidBalance: 0,
      };
      this.state.clientSearchText = `${c.firstname} ${c.lastname}`;
    }

    this.state.currency = tx.currency;
    this.state.selectedPaymentTermsId = tx.payment_terms ?? null;

    this.state.items = saleDetails.items.map(lineItem => {
      const prodPrice = lineItem.prod_price;
      const product: Product = {
        id: lineItem.product.id,
        name: lineItem.product.name,
        category: lineItem.product.category,
        price: parseFloat(lineItem.product.price),
        description: lineItem.product.description,
        disponibility: 0,  // unknown in edit context; server enforces
      };
      return {
        id: lineItem.id,
        selectedProduct: product,
        productSearchText: lineItem.product.name,
        quantity: lineItem.quantity,
        price: prodPrice,
        basePriceEUR: prodPrice,  // assume stored in transaction currency; best effort
        taxRateId: null,          // resolved below
        discountType: lineItem.discount_type,
        discountValue: lineItem.discount_value,
        lastSoldPrice: null,
        lastSoldCurrency: null,
      } as SaleLineItemFormState;
    });

    // Resolve tax rate IDs from rate names/percentages stored on line items
    this.state.items.forEach((item, idx) => {
      const detail = saleDetails.items[idx];
      if (detail.tax_rate_percent != null) {
        const matched = this.state.availableTaxRates.find(
          r => Math.abs(parseFloat(r.rate) - detail.tax_rate_percent!) < 0.001
        );
        item.taxRateId = matched ? matched.id : null;
      }
    });

    this.stateChange$.next();
  }

  // ======== Display helpers ========

  displayClient(client: Client | null): string {
    return client ? `${client.firstname} ${client.lastname}` : '';
  }

  displayProduct(product: Product | null): string {
    return product ? product.name : '';
  }

  filteredClients(): Client[] {
    if (!this.state.clientSearchText) return this.state.availableClients;
    const search = this.state.clientSearchText.toLowerCase();
    return this.state.availableClients.filter(
      c =>
        c.firstname.toLowerCase().includes(search) ||
        c.lastname.toLowerCase().includes(search)
    );
  }

  filteredProductsForItem(index: number): Product[] {
    const item = this.state.items[index];
    if (!item || !item.productSearchText) return this.state.availableProducts;
    const search = item.productSearchText.toLowerCase();
    return this.state.availableProducts.filter(p =>
      p.name.toLowerCase().includes(search)
    );
  }

  // ======== Legacy compatibility (state-passing overloads) ========
  // These accept the old SaleFormState shape so existing callers compile
  // while consuming components are migrated.  They delegate to internal state.

  /** @deprecated Use loadClients() without arguments */
  loadClientsLegacy(state: any): void {
    this.loadClients();
  }

  /** @deprecated Use loadProducts() without arguments */
  loadProductsLegacy(state: any): void {
    this.loadProducts();
  }
}
