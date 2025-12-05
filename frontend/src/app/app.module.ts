import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";

import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { LoginComponent } from "./views/login-view/login.component";
import { CustomMaterialModule } from "./material.modules";
import { MatListModule } from "@angular/material/list";
import { MatGridListModule } from "@angular/material/grid-list";
import { HTTP_INTERCEPTORS, HttpClientModule } from "@angular/common/http";
import { ReactiveFormsModule, FormsModule } from "@angular/forms";
import { LayoutComponent } from "./layout/layout.component";
import { MatSidenavModule } from "@angular/material/sidenav";
import { MatIconModule } from "@angular/material/icon";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatPaginatorModule } from "@angular/material/paginator";
import { MatMenuModule } from "@angular/material/menu";
import { MatDialogModule } from "@angular/material/dialog";
import { MatChipsModule } from "@angular/material/chips";
import { ChipsComponent } from "./shared/components/chips/chips.component";
import { MatStepperModule } from "@angular/material/stepper";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { SalesViewComponent } from "./views/sales-view/sales-view.component";
import { SalesTableComponent } from "./shared/components/sales-table/sales-table.component"; // Import MatFormFieldModule
import { MatTableModule } from "@angular/material/table";
import { ProductsViewComponent } from "./views/products-view/products-view.component";
import { MatSortModule } from "@angular/material/sort";
import { AddProductViewComponent } from "./views/add-product-view/add-product-view.component";
import { MatSelectModule } from "@angular/material/select";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatRadioModule } from "@angular/material/radio";
import { MatAutocompleteModule } from "@angular/material/autocomplete";
import { ProductDetailDialogComponent } from "./shared/components/dialogs/product-detail-dialog/product-detail-dialog.component";
import { ProductBuyDialogComponent } from "./shared/components/dialogs/product-buy-dialog/product-buy-dialog.component";
import { ProductTableComponent } from "./shared/components/product-table/product-table.component";

import { AuthInterceptor } from "./shared/services/auth-api/auth.interceptor";
import { ClientTableComponent } from "./shared/components/client-table/client-table.component";
import { ClientViewComponent } from "./views/clients-view/client-view.component";
import { ClientDetailsViewComponent } from "./views/client-details-view/client-details-view.component";
import { AddClientViewComponent } from "./views/add-client-view/add-client-view.component";
import { ConfirmDialogComponent } from "./dialogs/confirm-dialog/confirm-dialog.component";
import { EditPriceDialogComponent } from "./dialogs/edit-price-dialog/edit-price-dialog.component";
import { ReportsViewComponent } from "./views/reports-view/reports-view.component";

@NgModule({
  declarations: [
    AppComponent,
    LayoutComponent,
    LoginComponent,
    ProductsViewComponent,
    ClientViewComponent,
    AddProductViewComponent,
    ProductDetailDialogComponent,
    ProductBuyDialogComponent,
    EditPriceDialogComponent,
    ProductTableComponent,
    ClientTableComponent,
    ClientDetailsViewComponent,
    AddClientViewComponent,
    SalesViewComponent,
    ReportsViewComponent,
    ConfirmDialogComponent,
    EditPriceDialogComponent,
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
    ChipsComponent,
    MatMenuModule,
    MatDialogModule,
    MatChipsModule,
    MatStepperModule,
    MatProgressSpinnerModule,
    MatTableModule,
    MatSortModule,
    MatSelectModule,
    MatFormFieldModule,
    MatRadioModule,
    MatAutocompleteModule,
    SalesTableComponent,
  ],
  providers: [{ provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }],
  bootstrap: [AppComponent],
})
export class AppModule {}
