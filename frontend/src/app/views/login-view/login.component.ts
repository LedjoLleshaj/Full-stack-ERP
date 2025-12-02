import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";
import { LOCAL_STORAGE_KEYS } from "../../shared/constants";
import { FormControl, FormGroup, Validators } from "@angular/forms";
import { DarkModeService } from "../../shared/services/dark-mode/dark-mode.service";
import { AuthApiService } from "../../shared/services/auth-api/auth-api.service";
import { CookieService } from "../../shared/services/cookie.service";

@Component({
  selector: "app-login",
  templateUrl: "./login.component.html",
  styleUrls: ["./login.component.scss"],
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;

  constructor(
    private router: Router,
    private snackBar: MatSnackBar,
    public darkModeService: DarkModeService,
    private authService: AuthApiService
  ) {}

  ngOnInit() {
    // Clear any stale cookies from previous sessions
    CookieService.clearAuthCookies();
    
    this.loginForm = new FormGroup({
      username: new FormControl("", Validators.required),
      password: new FormControl("", Validators.minLength(4)),
    });
  }

  get username() {
    return this.loginForm.get("username");
  }

  get password() {
    return this.loginForm.get("password");
  }

  confirm() {
    this.authService.login(this.username?.value, this.password?.value).subscribe({
      next: (response) => {
        // Tokens are now stored as HttpOnly cookies by the backend
        // User info is stored in localStorage by the auth service
        this.router.navigate(["/products"]);
      },
      error: (error) => {
        this.snackBar.open("Username or password not correct");
      },
    });
  }
}
