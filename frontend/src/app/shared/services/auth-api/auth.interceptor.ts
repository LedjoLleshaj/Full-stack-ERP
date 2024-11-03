// auth.interceptor.ts
import { Injectable } from "@angular/core";
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from "@angular/common/http";
import { Observable } from "rxjs";
import { AuthApiService } from "./auth-api.service";

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthApiService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.authService.getToken();

    if (token) {
      console.log("auth token: interceptor", token); // Log auth token to console
      // Clone the request and add the Authorization header with 'Bearer' prefix
      const authReq = req.clone({
        headers: req.headers.set("Authorization", `Bearer ${token}`),
      });
      return next.handle(authReq);
    } else {
      return next.handle(req);
    }
  }
}
