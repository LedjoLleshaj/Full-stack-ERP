import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { LayoutComponent } from "./layout/layout.component";
import { LoginComponent } from "./login/login.component";
import { ProductsViewComponent } from "./products-view/products-view.component";
import { AddProductViewComponent } from "./add-product-view/add-product-view.component";
import { AuthGuard } from "./shared/auth.guard";
import { PublicGuard } from "./shared/public.guard";
import { SalesViewComponent } from "./sales-view/sales-view.component";
import { ClientViewComponent } from "./clients-view/client-view.component";

const routes: Routes = [
  {
    path: "",
    component: LayoutComponent,
    children: [
      {
        path: "",
        component: LoginComponent,
        title: "- Selita -",
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
        path: "products",
        component: ProductsViewComponent,
        title: "Products - Selita",
      },
      { path: "add-product", component: AddProductViewComponent },
    ],
    canActivate: [AuthGuard],
  },
  {
    path: "login",
    component: LoginComponent,
    canActivate: [PublicGuard],
    title: "Login - Selita",
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
