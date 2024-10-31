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
import { MatTableModule } from '@angular/material/table';
import { ProductsViewComponent } from './products-view/products-view.component';
import { MatSortModule } from '@angular/material/sort';
import { AddProductViewComponent } from './add-product-view/add-product-view.component';
import { MatSelectModule } from '@angular/material/select'; // Import MatSelectModule
import { MatFormFieldModule } from '@angular/material/form-field';
import { SalesViewComponent } from './sales-view/sales-view.component';
import { SalesTableComponent } from './shared/components/sales-table/sales-table.component'; // Import MatFormFieldModule

@NgModule({
  declarations: [
    AppComponent,
    LayoutComponent,
    LoginComponent,
    ProductsViewComponent,
    AddProductViewComponent,
    SalesViewComponent,
    SalesTableComponent
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
    MatFormFieldModule 
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
