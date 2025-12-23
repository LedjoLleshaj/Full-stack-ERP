import { Component } from "@angular/core";
import { FormBuilder, FormGroup, Validators } from "@angular/forms";
import { SupplierService } from "../../shared/services/suppliers-api/supplier.service";
import { Router } from "@angular/router";

@Component({
  selector: "app-add-supplier-view",
  templateUrl: "./add-supplier-view.component.html",
  styleUrls: ["./add-supplier-view.component.scss"],
})
export class AddSupplierViewComponent {
  supplierForm: FormGroup;

  constructor(private fb: FormBuilder, private supplierService: SupplierService, private router: Router) {
    this.supplierForm = this.fb.group({
      firstname: ["", Validators.required],
      lastname: ["", Validators.required],
      email: ["", [Validators.email]],
      phone: [""],
      address: ["", Validators.required],
    });
  }

  onSubmit() {
    if (this.supplierForm.valid) {
      console.log("Form submitted:", this.supplierForm.value);
      this.supplierService.addSupplier(this.supplierForm.value).subscribe({
        next: (response) => {
          console.log("Supplier added successfully:", response);
          this.router.navigate(["/suppliers"]);
        },
        error: (error) => {
          console.error("Error adding supplier:", error);
        },
      });
    }
  }
}
