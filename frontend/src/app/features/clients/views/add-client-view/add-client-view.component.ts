import { Component, OnInit } from "@angular/core";
import { FormBuilder, FormGroup, Validators } from "@angular/forms";
import { ClientService } from "../../../../shared/services/clients-api/client.service";
import { Router } from "@angular/router";

import { InventoryService } from "src/app/shared/services/inventory-api/inventory.service";

@Component({
  selector: "app-add-product-view",
  templateUrl: "./add-client-view.component.html",
  styleUrls: ["./add-client-view.component.scss"],
})
export class AddClientViewComponent {
  clientForm: FormGroup;

  constructor(private fb: FormBuilder, private clientService: ClientService, private router: Router) {
    this.clientForm = this.fb.group({
      firstname: ["", Validators.required],
      lastname: ["", Validators.required],
      email: ["", [Validators.email]],
      phone: ["", [Validators.required, Validators.pattern(/^\d{10}$/)]],
      address: ["", Validators.required],
      city: ["", Validators.required],
    });
  }

  onSubmit() {
    if (this.clientForm.valid) {
      console.log("Form submitted:", this.clientForm.value);
      this.clientService.addClient(this.clientForm.value).subscribe({
        next: (response) => {
          console.log("Client added successfully:", response);
          this.router.navigate(["/clients"]);
        },
        error: (error) => {
          console.error("Error adding client:", error);
        },
      });
    }
  }
}
