import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { LayoutComponent } from "./layout/layout.component";
import { LoginComponent } from "./login/login.component";
import { ProductsViewComponent } from "./products-view/products-view.component";
import { AuthGuard } from "./shared/auth.guard";
import { PublicGuard } from "./shared/public.guard";

const routes: Routes = [
  {
    path: "",
    component: LayoutComponent,
    children: [
      {
        path: "",
        component: LoginComponent,
        title: "Available Film - Selita",
      },
      {
        path: "history",
        component: LoginComponent,
        title: "Rental history - Selita",
      },
      {
        path: "products",
        component: ProductsViewComponent,
        title: "Products - Selita",
      },
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
