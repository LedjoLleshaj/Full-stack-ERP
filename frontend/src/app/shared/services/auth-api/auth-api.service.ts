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

  // Simulate login with a mock response
  login(username: string, password: string): Observable<LoginResponse> {
    // Mock token payload (base64-encoded), mimicking a real JWT
    const mockToken = btoa(
      JSON.stringify({ username: username, exp: Date.now() + 1000000 })
    );

    // Mock response object
    const mockResponse: LoginResponse = {
      token: `header.${mockToken}.signature`, // Mock JWT format: header.payload.signature
      first_name: "John", // Mock first name
      last_name: "Doe", // Mock last name
    };

    // Simulate a delay and return the mock response as an observable
    return of(mockResponse).pipe(delay(1000)); // Optional delay to simulate async
  }

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
