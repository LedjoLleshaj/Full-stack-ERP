import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Observable, BehaviorSubject, throwError, of } from "rxjs";
import { catchError, tap } from "rxjs/operators";
import { LoginResponse } from "../../../models/auth.model";
import { environment } from "src/environments/environment";
import { LOCAL_STORAGE_KEYS } from "../../constants";
import { Router } from "@angular/router";

export interface User {
  id: number;
  username: string;
  firstName: string;
  lastName: string;
}

@Injectable({
  providedIn: "root",
})
export class AuthApiService {
  private httpOptions = {
    headers: new HttpHeaders({ "Content-Type": "application/json" }),
    withCredentials: true, // Important for cookies
  };
  private apiUrl = environment.apiUrl;

  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    this.loadUserFromStorage();
  }

  private loadUserFromStorage(): void {
    // We can no longer check for tokens, so we rely on the user info in localStorage
    // or try to refresh the token to see if we are still logged in.
    const userIdStr = localStorage.getItem(LOCAL_STORAGE_KEYS.USER_ID);
    const username = localStorage.getItem(LOCAL_STORAGE_KEYS.USERNAME);
    const firstName = localStorage.getItem(LOCAL_STORAGE_KEYS.FIRST_NAME);
    const lastName = localStorage.getItem(LOCAL_STORAGE_KEYS.LAST_NAME);

    if (userIdStr && username && firstName && lastName) {
      this.currentUserSubject.next({
        id: parseInt(userIdStr, 10),
        username,
        firstName,
        lastName
      });
    }
  }

  login(username: string, password: string): Observable<LoginResponse> {
    const loginUrl = `${this.apiUrl}${environment.login}`;
    return this.http
      .post<LoginResponse>(loginUrl, { username, password }, this.httpOptions)
      .pipe(
        tap((response) => {
          this.setUserInfo(response);
        }),
        catchError(this.handleError<LoginResponse>("login"))
      );
  }

  refreshToken(): Observable<any> {
    return this.http
      .post<any>(
        `${this.apiUrl}${environment.refreshToken}`,
        {},
        this.httpOptions
      )
      .pipe(
        catchError((error) => {
          console.error("Error refreshing token:", error);
          this.logout();
          return throwError(() => error);
        })
      );
  }

  logout(): void {
    this.http.post(`${this.apiUrl}/logout`, {}, this.httpOptions).subscribe();
    
    Object.values(LOCAL_STORAGE_KEYS).forEach((key) => {
      if (key !== LOCAL_STORAGE_KEYS.DARK_MODE) {
        localStorage.removeItem(key);
      }
    });
    this.currentUserSubject.next(null);
    this.router.navigate(["/login"]);
  }

  isAuthenticated(): boolean {
    // With HttpOnly cookies, we can't check the token directly.
    // We rely on the presence of user info as a proxy for "logged in" state.
    // The actual API calls will fail if the cookie is invalid/expired.
    return !!this.currentUserSubject.value;
  }

  // Helper to get user info, not tokens
  getUser(): User | null {
    return this.currentUserSubject.value;
  }

  // Get the current user's ID for API requests
  getUserId(): number | null {
    return this.currentUserSubject.value?.id ?? null;
  }

  private setUserInfo(response: LoginResponse): void {
    localStorage.setItem(LOCAL_STORAGE_KEYS.USER_ID, response.user_id.toString());
    localStorage.setItem(LOCAL_STORAGE_KEYS.USERNAME, response.username);
    localStorage.setItem(LOCAL_STORAGE_KEYS.FIRST_NAME, response.first_name);
    localStorage.setItem(LOCAL_STORAGE_KEYS.LAST_NAME, response.last_name);

    this.currentUserSubject.next({
      id: response.user_id,
      username: response.username,
      firstName: response.first_name,
      lastName: response.last_name,
    });
  }

  private handleError<T>(operation = "operation", result?: T) {
    return (error: any): Observable<T> => {
      console.error(`${operation} failed: ${error.message}`);
      return throwError(() => error);
    };
  }
}
