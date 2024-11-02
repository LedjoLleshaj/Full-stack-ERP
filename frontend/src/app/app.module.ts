import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";

import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { LoginComponent } from "./login/login.component";
import { CustomMaterialModule } from "./material.modules";
import { MatListModule } from "@angular/material/list";
import { MatGridListModule } from "@angular/material/grid-list";
import { HttpClientModule } from "@angular/common/http";
import { ReactiveFormsModule, FormsModule } from "@angular/forms";
import { LayoutComponent } from "./layout/layout.component";
import { MatSidenavModule } from "@angular/material/sidenav";
import { MatIconModule } from "@angular/material/icon";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatPaginatorModule } from "@angular/material/paginator";
import { MatMenuModule } from "@angular/material/menu";
import { MatDialogModule } from "@angular/material/dialog";
import { MatChipsModule } from "@angular/material/chips";
import { MatStepperModule } from "@angular/material/stepper";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { SalesViewComponent } from "./sales-view/sales-view.component";
import { SalesTableComponent } from "./shared/components/sales-table/sales-table.component"; // Import MatFormFieldModule
import { MatTableModule } from "@angular/material/table";
import { ProductsViewComponent } from "./products-view/products-view.component";
import { MatSortModule } from "@angular/material/sort";
import { AddProductViewComponent } from "./add-product-view/add-product-view.component";
import { MatSelectModule } from "@angular/material/select";
import { MatFormFieldModule } from "@angular/material/form-field";
import { ProductDetailDialogComponent } from "./shared/components/dialogs/product-detail-dialog/product-detail-dialog.component";
import { ProductBuyDialogComponent } from "./shared/components/dialogs/product-buy-dialog/product-buy-dialog.component";
import { ProductTableComponent } from "./shared/components/product-table/product-table.component";

@NgModule({
  declarations: [
    AppComponent,
    LayoutComponent,
    LoginComponent,
    ProductsViewComponent,
    AddProductViewComponent,
    ProductDetailDialogComponent,
    ProductBuyDialogComponent,
    ProductTableComponent,
    AddProductViewComponent,
    SalesViewComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    CustomMaterialModule,
    MatListModule,
    MatGridListModule,
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule,
    MatSidenavModule,
    MatIconModule,
    MatSnackBarModule,
    MatPaginatorModule,
    MatMenuModule,
    MatDialogModule,
    MatChipsModule,
    MatStepperModule,
    MatProgressSpinnerModule,
    MatTableModule,
    MatSortModule,
    MatSelectModule,
    MatFormFieldModule,
    SalesTableComponent,
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
