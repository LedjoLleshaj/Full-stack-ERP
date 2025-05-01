import { Component, Inject } from "@angular/core";
import { MAT_DIALOG_DATA } from "@angular/material/dialog";

@Component({
  selector: "app-edit-price-dialog",
  templateUrl: "./edit-price-dialog.component.html",
})
export class EditPriceDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: any) {}
}
