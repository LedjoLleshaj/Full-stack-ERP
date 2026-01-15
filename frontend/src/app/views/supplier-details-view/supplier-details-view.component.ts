import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Supplier } from 'src/app/models/supplier.model';
import { SupplierService } from 'src/app/shared/services/suppliers-api/supplier.service';

@Component({
  selector: 'app-supplier-details-view',
  templateUrl: './supplier-details-view.component.html',
  styleUrls: ['./supplier-details-view.component.scss']
})
export class SupplierDetailsViewComponent implements OnInit {
  supplier: Supplier | null = null;
  isLoading = true;
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private supplierService: SupplierService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    const supplierId = this.route.snapshot.paramMap.get('id');
    if (supplierId) {
      this.loadSupplier(+supplierId);
    } else {
      this.errorMessage = 'ID e furnitorit mungon';
      this.isLoading = false;
    }
  }

  private loadSupplier(supplierId: number): void {
    this.isLoading = true;
    this.supplierService.getSupplierById(supplierId).subscribe({
      next: (data: Supplier) => {
        this.supplier = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load supplier:', err);
        this.errorMessage = 'Gabim në ngarkimin e furnitorit';
        this.isLoading = false;
        this.snackBar.open('Gabim në ngarkimin e furnitorit', 'Mbyll', { duration: 3000 });
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/suppliers']);
  }
}
