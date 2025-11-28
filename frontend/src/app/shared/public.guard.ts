import { Injectable } from "@angular/core";
import { Router } from "@angular/router";
import { AuthApiService } from "./services/auth-api/auth-api.service";

@Injectable({
  providedIn: "root",
})
export class PublicGuard {
  constructor(private router: Router, private authService: AuthApiService) {}

  canActivate(): boolean {
    if (this.authService.isAuthenticated()) {
      this.router.navigate(["/"]);
      return false;
    }
    return true;
  }
}
