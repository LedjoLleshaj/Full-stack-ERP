import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { LayoutComponent } from "./layout/layout.component";
import { LoginComponent } from "./views/login-view/login.component";
import { ProductsViewComponent } from "./views/products-view/products-view.component";
import { AddProductViewComponent } from "./views/add-product-view/add-product-view.component";
import { AuthGuard } from "./shared/auth.guard";
import { PublicGuard } from "./shared/public.guard";
import { SalesViewComponent } from "./views/sales-view/sales-view.component";
import { ClientViewComponent } from "./views/clients-view/client-view.component";
import { ClientDetailsViewComponent } from "./views/client-details-view/client-details-view.component";
import { AddClientViewComponent } from "./views/add-client-view/add-client-view.component";
import { ReportsViewComponent } from "./views/reports-view/reports-view.component";
import { RevenueViewComponent } from "./views/revenue-view/revenue-view.component";
import { PaidVsUnpaidViewComponent } from "./views/paid-vs-unpaid-view/paid-vs-unpaid-view.component";
import { TopProductsViewComponent } from "./views/top-products-view/top-products-view.component";
import { ProfitByCategoryViewComponent } from "./views/profit-by-category-view/profit-by-category-view.component";
import { AlertsViewComponent } from "./views/alerts-view/alerts-view.component";
import { SaleDetailsViewComponent } from "./views/sale-details-view/sale-details-view.component";
import { SupplierViewComponent } from "./views/suppliers-view/supplier-view.component";
import { AddSupplierViewComponent } from "./views/add-supplier-view/add-supplier-view.component";
import { TopClientsViewComponent } from "./views/top-clients-view/top-clients-view.component";
import { ProductDetailsViewComponent } from "./views/product-details-view/product-details-view.component";

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
      {
        path: "sales",
        component: SalesViewComponent,
        title: "Sale History - Selita",
      },
      {
        path: "clients",
        component: ClientViewComponent,
        title: "Client List - Selita",
      },
      {
        path: "suppliers",
        component: SupplierViewComponent,
        title: "Supplier List - Selita",
      },
      {
        path: "products",
        component: ProductsViewComponent,
        title: "Products - Selita",
      },
      {
        path: "reports",
        component: ReportsViewComponent,
        title: "Reports - Selita",
      },
      {
        path: "reports/revenue",
        component: RevenueViewComponent,
        title: "Revenue Trend - Selita",
      },
      {
        path: "reports/paid-vs-unpaid",
        component: PaidVsUnpaidViewComponent,
        title: "Paid vs Unpaid - Selita",
      },
      {
        path: "reports/top-products",
        component: TopProductsViewComponent,
        title: "Top Products - Selita",
      },
      {
        path: "reports/profit-by-category",
        component: ProfitByCategoryViewComponent,
        title: "Profit By Category - Selita",
      },
      {
        path: "reports/top-clients",
        component: TopClientsViewComponent,
        title: "Top Clients - Selita",
      },
      {
        path: "alerts",
        component: AlertsViewComponent,
        title: "Alerts - Selita",
      },
      {
        path: "client/:id",
        component: ClientDetailsViewComponent,
        title: "Client Details - Selita",
      },
      { path: "add-product", component: AddProductViewComponent },
      { path: "add-client", component: AddClientViewComponent },
      { path: "add-supplier", component: AddSupplierViewComponent },
      {
        path: "sale/:id",
        component: SaleDetailsViewComponent,
        title: "Sale Details - Selita",
      },
      {
        path: "product/:id",
        component: ProductDetailsViewComponent,
        title: "Product Details - Selita",
      },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
