import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Observable, of } from "rxjs";
import { catchError, tap } from "rxjs/operators";
import { LoginResponse, RefreshToken } from "../../../models/auth.model";
import { environment } from "../../../../environment/environments"; // Ensure correct path to environment
import { LOCAL_STORAGE_KEYS } from "../../constants";

@Injectable({
  providedIn: "root",
})
export class AuthApiService {
  // http options used for making API calls
  private httpOptions = {
    headers: new HttpHeaders({ "Content-Type": "application/json" }),
  };
  private apiUrl = environment.apiUrl; // Ensure that environment.apiUrl is properly defined

  // error messages received from the login attempt
  public errors: string[] = [];

  constructor(private http: HttpClient) {}

  // Send post request to login endpoint e.g., http://0.0.0.0:8080/selita/login
  login(username: string, password: string): Observable<LoginResponse> {
    const loginUrl = `${this.apiUrl}${environment.login}`; // Ensure that environment.apiUrl and environment.login are properly defined
    return this.http.post<LoginResponse>(loginUrl, { username, password }, this.httpOptions).pipe(
      catchError(this.handleError<LoginResponse>("login")) // Add error handling
    );
  }

  // auth-api.service.ts
  refreshToken(): Observable<any> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return of(null); // No refresh token available
    }

    return this.http
      .post(`${this.apiUrl}${environment.refreshToken}`, { refresh: refreshToken }, this.httpOptions)
      .pipe(
        tap((response: any) => {
          if (response.access) {
            localStorage.setItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN, response.access); // Update access token
          }
        }),
        catchError((error) => {
          console.error("Error refreshing token:", error);
          return of(null); // Return null or handle error accordingly
        })
      );
  }

  // Static logout method to clear localStorage except DARK_MODE
  static logout(): void {
    Object.values(LOCAL_STORAGE_KEYS).forEach((key) => {
      if (key !== LOCAL_STORAGE_KEYS.DARK_MODE) {
        localStorage.removeItem(key);
      }
    });
    window.location.reload();
  }

  // Error handling method for Http operations
  private handleError<T>(operation = "operation", result?: T) {
    return (error: any): Observable<T> => {
      console.error(`${operation} failed: ${error.message}`); // Log error to console

      // Keep app running by returning an empty result (or throw error based on preference)
      return of(result as T);
    };
  }
  getRefreshToken(): string {
    return localStorage.getItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN) ?? "";
  }

  getToken(): string {
    return localStorage.getItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN) ?? "";
  }
}
