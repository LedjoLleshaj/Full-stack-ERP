import { Injectable } from "@angular/core";
import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpErrorResponse,
} from "@angular/common/http";
import { Observable, throwError, BehaviorSubject } from "rxjs";
import { catchError, filter, take, switchMap } from "rxjs/operators";
import { AuthApiService } from "./auth-api.service";
import { environment } from "src/environments/environment";
import { CookieService } from "../cookie.service";

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  private refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(
    null
  );

  constructor(private authService: AuthApiService) {}

  intercept(
    req: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    let authReq = req;
    
    // We don't need to add the token manually anymore, but we must ensure credentials are sent
    if (req.url.startsWith(environment.apiUrl)) {
      authReq = req.clone({
        withCredentials: true
      });
    }

    return next.handle(authReq).pipe(
      catchError((error) => {
        if (
          error instanceof HttpErrorResponse &&
          (error.status === 401 || error.status === 403)
        ) {
          return this.handle401Error(authReq, next);
        } else {
          return throwError(() => error);
        }
      })
    );
  }

  private handle401Error(request: HttpRequest<any>, next: HttpHandler) {
    // If the failed request was a refresh token request, don't try to refresh again
    if (request.url.includes(environment.refreshToken)) {
      // Clear stale cookies when refresh fails
      CookieService.clearAuthCookies();
      this.authService.logout();
      return throwError(() => new Error("Refresh token expired"));
    }

    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshTokenSubject.next(null);

      return this.authService.refreshToken().pipe(
        switchMap(() => {
          this.isRefreshing = false;
          this.refreshTokenSubject.next(true); // Signal that refresh is done
          // Clone the request with credentials to ensure cookies are included
          const retryReq = request.clone({ withCredentials: true });
          return next.handle(retryReq); // Retry the original request
        }),
        catchError((err) => {
          this.isRefreshing = false;
          // Clear stale cookies when refresh fails
          CookieService.clearAuthCookies();
          this.authService.logout();
          return throwError(() => err);
        })
      );
    } else {
      return this.refreshTokenSubject.pipe(
        filter((token) => token != null),
        take(1),
        switchMap(() => {
          // Clone the request with credentials to ensure cookies are included
          const retryReq = request.clone({ withCredentials: true });
          return next.handle(retryReq);
        })
      );
    }
  }
}
