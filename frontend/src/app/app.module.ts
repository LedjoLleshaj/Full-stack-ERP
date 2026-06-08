import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { provideHttpClient, withInterceptorsFromDi } from "@angular/common/http";
import { ReactiveFormsModule, FormsModule } from "@angular/forms";

import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { CoreModule } from "./core";
import { LayoutComponent } from "./layout/layout.component";
import { LoginComponent } from "./views/login-view/login.component";
import { LandingPageComponent } from "./views/landing-page/landing-page.component";

// Dialogs (used globally)

// Material modules needed for Layout and Login
import { MatSidenavModule } from "@angular/material/sidenav";
import { MatListModule } from "@angular/material/list";
import { MatIconModule } from "@angular/material/icon";
import { MatMenuModule } from "@angular/material/menu";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatButtonModule } from "@angular/material/button";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatDialogModule } from "@angular/material/dialog";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatDividerModule } from "@angular/material/divider";
import { MatCardModule } from "@angular/material/card";

// ECharts for lazy-loaded modules
import { NgxEchartsModule } from "ngx-echarts";

@NgModule({ declarations: [
        AppComponent,
        LayoutComponent,
        LoginComponent,
        LandingPageComponent,
    ],
    bootstrap: [AppComponent], imports: [BrowserModule,
        AppRoutingModule,
        BrowserAnimationsModule,
        ReactiveFormsModule,
        FormsModule,
        CoreModule,
        // Material for Layout/Login
        MatSidenavModule,
        MatListModule,
        MatIconModule,
        MatMenuModule,
        MatSnackBarModule,
        MatButtonModule,
        MatFormFieldModule,
        MatInputModule,
        MatProgressSpinnerModule,
        MatDialogModule,
        MatToolbarModule,
        MatDividerModule,
        MatCardModule,
        // ECharts config (must be in root)
        NgxEchartsModule.forRoot({
            echarts: () => import('echarts')
        })], providers: [provideHttpClient(withInterceptorsFromDi())] })
export class AppModule {}
