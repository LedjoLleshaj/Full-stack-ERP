// auth.interceptor.ts
import { Injectable } from "@angular/core";
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from "@angular/common/http";
import { Observable, of } from "rxjs";
import { catchError, switchMap, tap } from "rxjs/operators";
import { AuthApiService } from "./auth-api.service";

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthApiService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.authService.getToken();

    let authReq = req;
    if (token) {
      // Clone the request and add the Authorization header with 'Bearer' prefix
      authReq = req.clone({
        headers: req.headers.set("Authorization", `Bearer ${token}`),
      });
    }

    return next.handle(authReq).pipe(
      catchError((error) => {
        // If the error is due to an expired token (401 or 403)s
        if (error.status === 401 || error.status === 403) {
          // Attempt to refresh the access token
          return this.authService.refreshToken().pipe(
            switchMap((newTokenResponse: any) => {
              // Clone the original request and set the new access token
              const newAuthReq = req.clone({
                headers: req.headers.set("Authorization", `Bearer ${newTokenResponse.access}`),
              });
              // Retry the original request with the new access token
              return next.handle(newAuthReq);
            }),
            catchError((err) => {
              // If refreshing the token fails, you may want to log out the user
              AuthApiService.logout();
              return of(err); // Return the original error
            })
          );
        } else {
          return of(error); // If the error is not a 401 or 403, just return the error
        }
      })
    );
  }
}
