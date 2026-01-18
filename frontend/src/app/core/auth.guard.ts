import { Injectable } from "@angular/core";
import { Router } from "@angular/router";
import { AuthApiService } from "../shared/services/auth-api/auth-api.service";

@Injectable({
  providedIn: "root",
})
export class AuthGuard {
  constructor(private router: Router, private authService: AuthApiService) {}

  canActivate(): boolean {
    if (!this.authService.isAuthenticated()) {
      this.router.navigate(["/login"]);
      return false;
    }
    return true;
  }
}
