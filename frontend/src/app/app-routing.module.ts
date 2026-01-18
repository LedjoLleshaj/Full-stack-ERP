import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { LayoutComponent } from "./layout/layout.component";
import { LoginComponent } from "./views/login-view/login.component";
import { AuthGuard, PublicGuard } from "./core";

const routes: Routes = [
  {
    path: "login",
    component: LoginComponent,
    canActivate: [PublicGuard],
    title: "Login - Selita",
  },
  {
    path: "",
    component: LayoutComponent,
    canActivate: [AuthGuard],
    children: [
      {
        path: "",
        redirectTo: "sales",
        pathMatch: "full",
      },
      // Lazy-loaded feature modules
      {
        path: "sales",
        loadChildren: () => import("./features/sales/sales.module").then(m => m.SalesModule),
      },
      {
        path: "sale",
        loadChildren: () => import("./features/sales/sales.module").then(m => m.SalesModule),
      },
      {
        path: "restocks",
        loadChildren: () => import("./features/sales/restocks.module").then(m => m.RestocksModule),
      },
      {
        path: "restock",
        loadChildren: () => import("./features/sales/restocks.module").then(m => m.RestocksModule),
      },
      {
        path: "clients",
        loadChildren: () => import("./features/clients/clients.module").then(m => m.ClientsModule),
      },
      {
        path: "client",
        loadChildren: () => import("./features/clients/clients.module").then(m => m.ClientsModule),
      },
      {
        path: "products",
        loadChildren: () => import("./features/products/products.module").then(m => m.ProductsModule),
      },
      {
        path: "product",
        loadChildren: () => import("./features/products/products.module").then(m => m.ProductsModule),
      },
      {
        path: "add-product",
        redirectTo: "products/add",
        pathMatch: "full",
      },
      {
        path: "reports",
        loadChildren: () => import("./features/reports/reports.module").then(m => m.ReportsModule),
      },
      {
        path: "alerts",
        loadChildren: () => import("./features/reports/reports.module").then(m => m.ReportsModule),
      },
      {
        path: "suppliers",
        loadChildren: () => import("./features/suppliers/suppliers.module").then(m => m.SuppliersModule),
      },
      {
        path: "supplier",
        loadChildren: () => import("./features/suppliers/suppliers.module").then(m => m.SuppliersModule),
      },
      {
        path: "add-supplier",
        redirectTo: "suppliers/add",
        pathMatch: "full",
      },
      {
        path: "add-client",
        redirectTo: "clients/add",
        pathMatch: "full",
      },
      {
        path: "add-sale",
        redirectTo: "sales/add",
        pathMatch: "full",
      },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
