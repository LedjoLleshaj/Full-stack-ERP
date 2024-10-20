import { Injectable } from "@angular/core";
import { of, Observable } from "rxjs";
import { delay } from "rxjs/operators"; // Optional: to simulate API delay
import { LoginResponse } from "../../../models/auth.model";

import { LOCAL_STORAGE_KEYS } from "../../constants";

@Injectable({
  providedIn: "root",
})
export class AuthApiService {
  constructor() {}

  // Send post request to login endpoint 0.0.0.0:8080/selita/login
  login(username: string, password: string): Observable<LoginResponse> {}

  // Logout method to clear localStorage except DARK_MODE
  static logout() {
    Object.values(LOCAL_STORAGE_KEYS).forEach((key) => {
      if (key !== LOCAL_STORAGE_KEYS.DARK_MODE) {
        localStorage.removeItem(key);
      }
    });
    window.location.reload();
  }
}
