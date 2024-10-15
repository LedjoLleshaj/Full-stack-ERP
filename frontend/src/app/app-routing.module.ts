import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { LayoutComponent } from "./layout/layout.component";
import { LoginComponent } from "./login/login.component";
import { AuthGuard } from "./shared/auth.guard";
import { PublicGuard } from "./shared/public.guard";

const routes: Routes = [
  {
    path: "",
    component: LayoutComponent,
    children: [
      {
        path: "",
        title: "Available Film - Selita",
      },
      {
        path: "history",
        title: "Rental histoy - Selita",
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
