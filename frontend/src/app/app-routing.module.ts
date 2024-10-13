import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LayoutComponent } from './layout/layout.component';
import { LoginComponent } from './login/login.component';
import { AuthGuard } from './shared/auth.guard';
import { FilmViewComponent } from './film-view/film-view.component';
import { HistoryViewComponent } from './history-view/history-view.component';
import { PublicGuard } from './shared/public.guard';

const routes: Routes = [
  {
    path: '', component: LayoutComponent,
    children: [
      { path: '', component: FilmViewComponent, title: 'Available Film - Rentflix' },
      { path: 'history', component: HistoryViewComponent, title: 'Rental histoy - Rentflix' }
    ],
    canActivate: [AuthGuard]

  },
  { path: 'login', component: LoginComponent, canActivate: [PublicGuard], title: 'Login - Rentflix' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
