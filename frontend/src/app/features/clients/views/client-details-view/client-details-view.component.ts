import { Component, OnInit, OnDestroy } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";
import { Subscription } from "rxjs";
import * as XLSX from 'xlsx';

import { Client } from "../../../../models/client.model";
import { Product } from "../../../../models/product.model";
import { ClientService } from "src/app/shared/services/clients-api/client.service";
import { SaleFormService, SaleFormState } from "src/app/shared/services/sale-form/sale-form.service";

@Component({
  selector: "app-client-details-view",
  templateUrl: "./client-details-view.component.html",
  styleUrls: ["./client-details-view.component.scss"],
})
export class ClientDetailsViewComponent implements OnInit, OnDestroy {
  // Client info
  client: Client | undefined;
  clientId!: number;

  // Sale form state managed by service
  state: SaleFormState;

  // Expose service constants to template
  get paymentMethods(): string[] { return this.saleFormService.paymentMethods; }
  get currencies(): string[] { return this.saleFormService.currencies; }

  // Recent sales (client-specific)
  recentSales: any[] = [];
  isLoadingSales = false;
  isExporting = false;
  salesColumns = ['date', 'product_name', 'quantity', 'price', 'status'];

  // Edit/Delete state
  isEditing = false;
  isSaving = false;
  isDeleting = false;
  editForm: Partial<Client> = {};

  private stateChangeSub?: Subscription;

  constructor(
    private route: ActivatedRoute,
    private clientService: ClientService,
    private saleFormService: SaleFormService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {
    this.state = this.saleFormService.getInitialState();
  }

  ngOnInit() {
    this.clientId = Number(this.route.snapshot.paramMap.get("id"));
    if (this.clientId) {
      this.loadClient(this.clientId);
      this.loadClientSales(this.clientId);
    }

    // Subscribe to state changes for change detection
    this.stateChangeSub = this.saleFormService.onStateChange.subscribe(() => {
      // Trigger change detection if needed
    });

    this.saleFormService.loadProducts(this.state);
  }

  ngOnDestroy() {
    this.stateChangeSub?.unsubscribe();
  }

  // ========= CLIENT METHODS =========
  private loadClient(clientId: number): void {
    this.clientService.getClientById(clientId).subscribe({
      next: (data: Client) => {
        this.client = data;
      },
      error: (err) => {
        console.error("Failed to load client:", err);
        this.snackBar.open("Gabim ne ngarkimin e klientit", "Mbyll", { duration: 3000 });
      },
    });
  }

  private loadClientSales(clientId: number): void {
    this.isLoadingSales = true;
    this.clientService.getClientSales(clientId).subscribe({
      next: (data: any[]) => {
        // Filter to only unpaid sales (PENDING or PARTIAL), take last 10
        this.recentSales = data
          .filter(sale => sale.payment_status !== 'COMPLETED')
          .slice(0, 10);
        this.isLoadingSales = false;
      },
      error: (err) => {
        console.error('Failed to load client sales:', err);
        this.isLoadingSales = false;
      }
    });
  }

  // ========= PRODUCT/SALE METHODS (Delegated to Service) =========
  filteredProducts(): Product[] {
    return this.saleFormService.filteredProducts(this.state);
  }

  onProductSelect(event: any): void {
    const product = event.option.value;
    this.saleFormService.onProductSelect(this.state, product, this.clientId);
  }

  displayProduct(product: Product | null): string {
    return this.saleFormService.displayProduct(product);
  }

  enforceMax(event: any): void {
    const input = event.target as HTMLInputElement;
    const value = this.saleFormService.enforceMaxQuantity(this.state, input.value);
    input.value = String(value);
  }

  onCurrencyChange(): void {
    this.saleFormService.onCurrencyChange(this.state);
  }

  getTotal(): number {
    return this.saleFormService.getTotal(this.state);
  }

  canCreateSale(): boolean {
    return this.saleFormService.canCreateSale(this.state, this.clientId);
  }

  createSale(): void {
    this.saleFormService.createSale(this.state, this.clientId, false).subscribe({
      next: (success) => {
        if (success) {
          this.saleFormService.clearSelection(this.state);
          this.saleFormService.loadProducts(this.state);
          this.loadClient(this.clientId);
          this.loadClientSales(this.clientId);
        }
      }
    });
  }

  clearSelection(): void {
    this.saleFormService.clearSelection(this.state);
  }

  // ========= SALES TABLE HELPERS =========
  // Used by Excel export - kept for non-template usage
  formatSaleDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('sq-AL', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  // Used by Excel export - kept for non-template usage
  getSaleStatusLabel(status: string): string {
    const labels: { [key: string]: string } = {
      'COMPLETED': 'Paguar',
      'PARTIAL': 'Pjesërisht',
      'PENDING': 'Pa Paguar'
    };
    return labels[status] || status;
  }

  goToSale(saleId: number): void {
    this.router.navigate(['/sale', saleId]);
  }

  // ========= EXCEL EXPORT =========
  exportToExcel(): void {
    if (!this.client) return;
    
    this.isExporting = true;
    const clientName = `${this.client.firstname}_${this.client.lastname}`.replace(/\s+/g, '_');
    
    // Fetch ALL sales for this client (not just unpaid)
    this.clientService.getClientSales(this.clientId).subscribe({
      next: (allSales) => {
        // Transform sales to export format with autoincrement
        let num = 1;
        const exportData = allSales.map(s => ({
          'Num': num++,
          'ID': s.id,
          'Data': this.formatSaleDate(s.sale_date),
          'Produkti': s.product?.name || 'N/A',
          'Kategoria': s.product?.category || 'N/A',
          'Sasia (kg)': s.quantity,
          'Cmimi': s.prod_price,
          'Valuta': s.currency || 'EUR',
          'Totali': (s.quantity * s.prod_price).toFixed(2),
          'Statusi': this.getSaleStatusLabel(s.payment_status)
        }));

        if (exportData.length === 0) {
          this.snackBar.open('Nuk ka shitje për të eksportuar', 'Mbyll', { duration: 3000 });
          this.isExporting = false;
          return;
        }

        // Create workbook and worksheet
        const worksheet = XLSX.utils.json_to_sheet(exportData);
        const workbook = XLSX.utils.book_new();
        
        // Auto-size columns
        const columnWidths = this.getColumnWidths(exportData);
        worksheet['!cols'] = columnWidths;
        
        // Apply red background to unpaid status cells
        const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1');
        const statusColIndex = 9; // 'Statusi' is the 10th column (0-indexed = 9)
        
        for (let row = 1; row <= range.e.r; row++) { // Skip header row (row 0)
          const statusCellRef = XLSX.utils.encode_cell({ r: row, c: statusColIndex });
          const statusCell = worksheet[statusCellRef];
          
          if (statusCell && (statusCell.v === 'Pa Paguar' || statusCell.v === 'Pjesërisht')) {
            // Apply red background style
            statusCell.s = {
              fill: {
                patternType: 'solid',
                fgColor: { rgb: 'FFCCCC' } // Light red
              },
              font: {
                color: { rgb: 'CC0000' } // Dark red text
              }
            };
          }
        }
        
        // Add worksheet to workbook
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Shitjet');
        
        // Generate filename with client name and date
        const filename = `shitje_${clientName}_${new Date().toISOString().split('T')[0]}.xlsx`;
        
        // Write and download (use bookType with cellStyles for styling support)
        XLSX.writeFile(workbook, filename, { cellStyles: true });
        
        this.isExporting = false;
        this.snackBar.open('Raporti u shkarkua me sukses', 'Mbyll', { duration: 3000 });
      },
      error: (err) => {
        console.error('Failed to export sales:', err);
        this.snackBar.open('Gabim gjatë eksportimit', 'Mbyll', { duration: 3000 });
        this.isExporting = false;
      }
    });
  }

  private getColumnWidths(data: any[]): { wch: number }[] {
    if (!data || data.length === 0) return [];
    
    const headers = Object.keys(data[0]);
    return headers.map(header => {
      const maxLength = Math.max(
        header.length,
        ...data.map(row => String(row[header] || '').length)
      );
      return { wch: Math.min(maxLength + 2, 50) };
    });
  }

  // ========= EDIT/DELETE METHODS =========
  toggleEdit(): void {
    this.isEditing = !this.isEditing;
    if (this.isEditing && this.client) {
      // Populate form with current values
      this.editForm = {
        firstname: this.client.firstname,
        lastname: this.client.lastname,
        email: this.client.email,
        phone: this.client.phone,
        address: this.client.address,
        city: this.client.city
      };
    }
  }

  saveEdit(): void {
    if (!this.client || !this.clientId) return;

    this.isSaving = true;
    const updatedClient: Client = {
      ...this.client,
      ...this.editForm
    } as Client;

    this.clientService.updateClient(this.clientId, updatedClient).subscribe({
      next: (result) => {
        this.client = result;
        this.isEditing = false;
        this.isSaving = false;
        this.snackBar.open('Klienti u përditësua me sukses', 'Mbyll', { duration: 3000 });
      },
      error: (err) => {
        console.error('Failed to update client:', err);
        this.isSaving = false;
        this.snackBar.open('Gabim në përditësimin e klientit', 'Mbyll', { duration: 3000 });
      }
    });
  }

  confirmDelete(): void {
    const confirmed = window.confirm(
      `Jeni të sigurt që dëshironi të fshini klientin "${this.client?.firstname} ${this.client?.lastname}"?\n\Ky veprim është i pakthyeshëm. Të dhënat e klientit do të ruhen në shënime të transaksioneve.`
    );

    if (confirmed) {
      this.deleteClient();
    }
  }

  private deleteClient(): void {
    if (!this.clientId) return;

    this.isDeleting = true;
    this.clientService.deleteClient(this.clientId).subscribe({
      next: (result) => {
        this.snackBar.open(`Klienti u fshi. ${result.preserved_records} transaksione u përditësuan.`, 'Mbyll', { duration: 4000 });
        this.router.navigate(['/clients']);
      },
      error: (err) => {
        console.error('Failed to delete client:', err);
        this.isDeleting = false;
        this.snackBar.open('Gabim në fshirjen e klientit', 'Mbyll', { duration: 3000 });
      }
    });
  }
}
