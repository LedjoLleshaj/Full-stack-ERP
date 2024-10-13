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
import { MatSidenavModule } from "@angular/material/sidenav";
import { MatIconModule } from "@angular/material/icon";
import { MatSnackBarModule } from "@angular/material/snack-bar";

import { MatPaginatorModule } from "@angular/material/paginator";
import { MatMenuModule } from "@angular/material/menu";
import { MatDialogContent, MatDialogModule } from "@angular/material/dialog";
import { MatChipsModule } from "@angular/material/chips";
import { MatStepperModule } from "@angular/material/stepper";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";

@NgModule({
  declarations: [AppComponent, LoginComponent],
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
    FormsModule,
    MatPaginatorModule,
    MatMenuModule,
    MatDialogModule,
    MatChipsModule,
    MatStepperModule,
    MatProgressSpinnerModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
