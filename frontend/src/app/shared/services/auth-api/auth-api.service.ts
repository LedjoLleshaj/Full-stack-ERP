import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Observable, of } from "rxjs";
import { catchError } from "rxjs/operators";
import { LoginResponse } from "../../../models/auth.model";
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

  // error messages received from the login attempt
  public errors: string[] = [];

  constructor(private http: HttpClient) {}

  // Send post request to login endpoint e.g., http://0.0.0.0:8080/selita/login
  login(username: string, password: string): Observable<LoginResponse> {
    console.log("auth: ", username, password); // Log username and password to console
    const loginUrl = `${environment.apiUrl}${environment.login}`; // Ensure that environment.apiUrl and environment.login are properly defined
    return this.http.post<LoginResponse>(loginUrl, { username, password }, this.httpOptions).pipe(
      catchError(this.handleError<LoginResponse>("login")) // Add error handling
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
}
