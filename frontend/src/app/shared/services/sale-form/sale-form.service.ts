import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { Observable, Subject } from 'rxjs';

import { Client } from 'src/app/models/client.model';
import { Product } from 'src/app/models/product.model';
import { ClientService } from '../clients-api/client.service';
import { ProductService } from '../product-api/product.service';
import { SalesApiService } from '../sales-api/sales-api.service';
import { CurrencyExchangeService } from '../currency-exchange/currency-exchange.service';
import { PaymentTermsApiService } from '../payment-terms-api/payment-terms-api.service';
import { TaxRateApiService } from '../tax-rate-api/tax-rate-api.service';
import { AuthApiService } from '../auth-api/auth-api.service';
import { PaymentTerms } from '../../../models/payment-terms.model';
import { TaxRate } from '../../../models/tax-rate.model';

/**
 * Shared state for sale form across multiple components.
 * This interface represents all the data needed to create a sale.
 */
export interface SaleFormState {
  // Client selection
  availableClients: Client[];
  selectedClient: Client | null;
  clientSearchText: string;

  // Product selection
  availableProducts: Product[];
  selectedProduct: Product | null;
  productSearchText: string;

  // Sale details
  saleQuantity: number;
  salePrice: number;
  basePriceEUR: number;
  isPaid: boolean;
  lastSoldPrice: number | null;
  lastSoldCurrency: string | null;

  // Discount
  discountType: string | null;
  discountValue: number;

  // Payment options
  paymentMethod: string;
  currency: string;

  // Tax
  availableTaxRates: TaxRate[];
  selectedTaxRateId: number | null;

  // Payment terms
  availablePaymentTerms: PaymentTerms[];
  selectedPaymentTermsId: number | null;

  // UI state
  isSubmitting: boolean;
}

/**
 * Service to centralize sale creation logic that was duplicated across
 * AddSaleViewComponent and ClientDetailsViewComponent.
 */
@Injectable({
  providedIn: 'root'
})
export class SaleFormService {
  // Constants
  readonly paymentMethods: string[] = ['CASH', 'CARD'];
  readonly currencies: string[] = ['EUR', 'USD', 'LEK'];

  // State change notification
  private stateChange$ = new Subject<void>();
  onStateChange = this.stateChange$.asObservable();

  constructor(
    private clientService: ClientService,
    private productService: ProductService,
    private saleService: SalesApiService,
    private currencyExchange: CurrencyExchangeService,
    private paymentTermsService: PaymentTermsApiService,
    private taxRateService: TaxRateApiService,
    private authService: AuthApiService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  /**
   * Creates a fresh/reset form state
   */
  getInitialState(): SaleFormState {
    return {
      availableClients: [],
      selectedClient: null,
      clientSearchText: '',
      availableProducts: [],
      selectedProduct: null,
      productSearchText: '',
      saleQuantity: 1,
      salePrice: 0,
      basePriceEUR: 0,
      isPaid: true,
      lastSoldPrice: null,
      lastSoldCurrency: null,
      discountType: null,
      discountValue: 0,
      availableTaxRates: [],
      selectedTaxRateId: null,
      availablePaymentTerms: [],
      selectedPaymentTermsId: null,
      paymentMethod: 'CASH',
      currency: 'EUR',
      isSubmitting: false,
    };
  }

  /**
   * Loads available clients into the state
   */
  loadClients(state: SaleFormState): void {
    this.clientService.getClients().subscribe({
      next: (clients) => {
        state.availableClients = clients;
        this.stateChange$.next();
      },
      error: (err) => {
        console.error('Failed to fetch clients:', err);
        this.snackBar.open('Gabim ne ngarkimin e klienteve', 'Mbyll', { duration: 3000 });
      },
    });
  }

  /**
   * Loads available products (with stock > 0) into the state
   */
  loadProducts(state: SaleFormState): void {
    this.productService.getProducts().subscribe({
      next: (products) => {
        state.availableProducts = products.filter(p => p.disponibility > 0);
        this.stateChange$.next();
      },
      error: (err) => {
        console.error('Failed to fetch products:', err);
        this.snackBar.open('Gabim ne ngarkimin e produkteve', 'Mbyll', { duration: 3000 });
      },
    });
  }

  /**
   * Filters clients based on search text
   */
  filteredClients(state: SaleFormState): Client[] {
    if (!state.clientSearchText) {
      return state.availableClients;
    }
    const search = state.clientSearchText.toLowerCase();
    return state.availableClients.filter(
      c => c.firstname.toLowerCase().includes(search) || c.lastname.toLowerCase().includes(search)
    );
  }

  /**
   * Filters products based on search text
   */
  filteredProducts(state: SaleFormState): Product[] {
    if (!state.productSearchText) {
      return state.availableProducts;
    }
    return state.availableProducts.filter(p =>
      p.name.toLowerCase().includes(state.productSearchText.toLowerCase())
    );
  }

  /**
   * Handles client selection from autocomplete
   */
  onClientSelect(state: SaleFormState, client: Client): void {
    state.selectedClient = client;
    state.clientSearchText = `${client.firstname} ${client.lastname}`;
    state.lastSoldPrice = null;
    state.lastSoldCurrency = null;

    if (state.selectedProduct?.id && state.selectedClient?.id) {
      this.fetchLastSoldPrice(state);
    }
    this.stateChange$.next();
  }

  /**
   * Handles product selection from autocomplete
   */
  onProductSelect(state: SaleFormState, product: Product, clientId?: number): void {
    state.selectedProduct = product;
    state.salePrice = product.price;
    state.basePriceEUR = product.price;
    state.currency = 'EUR';
    state.saleQuantity = 1;
    state.productSearchText = product.name;

    // Fetch last sold price if client is available
    const targetClientId = clientId ?? state.selectedClient?.id;
    if (targetClientId && product.id) {
      this.fetchLastSoldPriceForClient(state, targetClientId, product.id);
    }
    this.stateChange$.next();
  }

  /**
   * Fetches last sold price for a client/product combination
   */
  fetchLastSoldPrice(state: SaleFormState): void {
    if (!state.selectedClient?.id || !state.selectedProduct?.id) return;
    this.fetchLastSoldPriceForClient(state, state.selectedClient.id, state.selectedProduct.id);
  }

  private fetchLastSoldPriceForClient(state: SaleFormState, clientId: number, productId: number): void {
    this.saleService.getLastSoldPrice(clientId, productId).subscribe({
      next: (response) => {
        state.lastSoldPrice = response.price;
        state.lastSoldCurrency = response.currency;
        this.stateChange$.next();
      },
      error: (err) => {
        console.error('Failed to fetch last sold price:', err);
        state.lastSoldPrice = null;
        state.lastSoldCurrency = null;
      },
    });
  }

  /**
   * Handles currency change - converts price from EUR to selected currency
   */
  onCurrencyChange(state: SaleFormState): void {
    if (!state.selectedProduct || state.basePriceEUR === 0) return;

    if (state.currency === 'EUR') {
      state.salePrice = state.basePriceEUR;
      this.stateChange$.next();
    } else {
      this.currencyExchange.getExchangeRate('EUR', state.currency).subscribe({
        next: (rate) => {
          state.salePrice = Math.round(state.basePriceEUR * rate * 100) / 100;
          this.stateChange$.next();
        },
        error: () => {
          this.snackBar.open('Gabim në marrjen e kursit të këmbimit', 'Mbyll', { duration: 3000 });
        },
      });
    }
  }

  /**
   * Enforces maximum quantity based on product availability
   */
  enforceMaxQuantity(state: SaleFormState, inputValue: string): number {
    const max = state.selectedProduct?.disponibility ?? 0;
    let value = parseInt(inputValue, 10) || 0;

    if (value > max) {
      value = max;
    }
    state.saleQuantity = value;
    return value;
  }

  /**
   * Calculates total sale amount (subtotal before tax)
   */
  getTotal(state: SaleFormState): number {
    return state.salePrice * state.saleQuantity;
  }

  loadPaymentTerms(state: SaleFormState): void {
    this.paymentTermsService.getPaymentTerms().subscribe({
      next: (terms) => {
        state.availablePaymentTerms = terms;
        this.stateChange$.next();
      },
      error: (err) => {
        console.error('Failed to fetch payment terms:', err);
      },
    });
  }

  /**
   * Loads available tax rates into the state
   */
  loadTaxRates(state: SaleFormState): void {
    this.taxRateService.getTaxRates().subscribe({
      next: (rates) => {
        state.availableTaxRates = rates;
        const defaultRate = rates.find(r => r.is_default);
        if (defaultRate) {
          state.selectedTaxRateId = defaultRate.id;
        }
        this.stateChange$.next();
      },
      error: (err) => {
        console.error('Failed to fetch tax rates:', err);
      },
    });
  }

  getDiscountAmount(state: SaleFormState): number {
    if (!state.discountType || state.discountValue <= 0) return 0;
    const subtotal = this.getTotal(state);
    if (state.discountType === 'PERCENT') {
      return Math.round(subtotal * state.discountValue / 100 * 100) / 100;
    }
    return Math.min(state.discountValue, subtotal);
  }

  getDiscountedSubtotal(state: SaleFormState): number {
    return this.getTotal(state) - this.getDiscountAmount(state);
  }

  getTaxAmount(state: SaleFormState): number {
    if (!state.selectedTaxRateId) return 0;
    const rate = state.availableTaxRates.find(r => r.id === state.selectedTaxRateId);
    if (!rate) return 0;
    const discountedSubtotal = this.getDiscountedSubtotal(state);
    return Math.round(discountedSubtotal * parseFloat(rate.rate) / 100 * 100) / 100;
  }

  getTotalWithTax(state: SaleFormState): number {
    return this.getDiscountedSubtotal(state) + this.getTaxAmount(state);
  }

  /**
   * Validates if sale can be created
   */
  canCreateSale(state: SaleFormState, clientId?: number): boolean {
    const effectiveClientId = clientId ?? state.selectedClient?.id;
    return (
      effectiveClientId != null &&
      state.selectedProduct != null &&
      state.saleQuantity > 0 &&
      state.saleQuantity <= state.selectedProduct.disponibility &&
      state.salePrice > 0 &&
      !state.isSubmitting
    );
  }

  /**
   * Creates a new sale
   */
  createSale(state: SaleFormState, clientId?: number, navigateOnSuccess: boolean = true): Observable<boolean> {
    const result = new Subject<boolean>();

    const effectiveClientId = clientId ?? state.selectedClient?.id;
    if (!this.canCreateSale(state, effectiveClientId) || !state.selectedProduct) {
      result.next(false);
      result.complete();
      return result.asObservable();
    }

    state.isSubmitting = true;
    const total = this.getTotalWithTax(state);
    const userId = this.authService.getUserId();

    if (!userId) {
      this.snackBar.open('Gabim: Përdoruesi nuk u gjet', 'Mbyll', { duration: 3000 });
      state.isSubmitting = false;
      result.next(false);
      result.complete();
      return result.asObservable();
    }

    const newSale: any = {
      prod: state.selectedProduct.id,
      prod_price: state.salePrice,
      quantity: state.saleQuantity,
      user: userId,
      client_id: effectiveClientId,
      currency: state.currency,
    };

    if (state.selectedTaxRateId) {
      newSale.tax_rate_id = state.selectedTaxRateId;
    }

    if (state.discountType && state.discountValue > 0) {
      newSale.discount_type = state.discountType;
      newSale.discount_value = state.discountValue;
    }

    if (state.selectedPaymentTermsId) {
      newSale.payment_terms_id = state.selectedPaymentTermsId;
    }

    if (state.isPaid) {
      newSale.payment = {
        amount: total,
        currency: state.currency,
        payment_method: state.paymentMethod,
        notes: `Payment for sale of ${state.saleQuantity} ${state.selectedProduct.name}`,
      };
    }

    this.saleService.createSale(newSale).subscribe({
      next: (response) => {
        console.log('Sale created successfully:', response);
        const statusMsg = response.transaction_status === 'COMPLETED' ? 'dhe u pagua' : '';
        this.snackBar.open(`Shitja u krijua me sukses ${statusMsg}!`, 'Mbyll', { duration: 3000 });
        state.isSubmitting = false;
        
        if (navigateOnSuccess) {
          this.router.navigate(['/sales']);
        }
        
        result.next(true);
        result.complete();
      },
      error: (error) => {
        console.error('Error creating sale:', error);
        const errorMsg = error?.error?.error || 'Gabim ne krijimin e shitjes';
        this.snackBar.open(errorMsg, 'Mbyll', { duration: 5000 });
        state.isSubmitting = false;
        result.next(false);
        result.complete();
      },
    });

    return result.asObservable();
  }

  /**
   * Clears/resets the form state
   */
  clearSelection(state: SaleFormState): void {
    state.selectedClient = null;
    state.clientSearchText = '';
    state.selectedProduct = null;
    state.productSearchText = '';
    state.saleQuantity = 1;
    state.salePrice = 0;
    state.basePriceEUR = 0;
    state.isPaid = true;
    state.lastSoldPrice = null;
    state.lastSoldCurrency = null;
    state.discountType = null;
    state.discountValue = 0;
    const defaultRate = state.availableTaxRates.find(r => r.is_default);
    state.selectedTaxRateId = defaultRate ? defaultRate.id : null;
    state.selectedPaymentTermsId = null;
    state.paymentMethod = 'CASH';
    state.currency = 'EUR';
    this.stateChange$.next();
  }

  /**
   * Display helpers
   */
  displayClient(client: Client | null): string {
    return client ? `${client.firstname} ${client.lastname}` : '';
  }

  displayProduct(product: Product | null): string {
    return product ? product.name : '';
  }
}
