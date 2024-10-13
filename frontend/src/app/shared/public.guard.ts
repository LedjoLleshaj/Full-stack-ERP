import { Injectable } from "@angular/core";
import { Router } from "@angular/router";
import { LOCAL_STORAGE_KEYS } from "./constants";

@Injectable({
  providedIn: "root",
})
export class PublicGuard {
  constructor(private router: Router) {}

  canActivate(): boolean {
    if (localStorage.getItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN) !== null) {
      this.router.navigate(["/"]);
      return false;
    }
    return true;
  }
}
