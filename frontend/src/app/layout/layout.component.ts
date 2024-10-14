import { MediaMatcher } from "@angular/cdk/layout";
import { ChangeDetectorRef, Component, ViewChild } from "@angular/core";
import { Router } from "@angular/router";
import { LOCAL_STORAGE_KEYS } from "../shared/constants";
import { DarkModeService } from "../shared/services/dark-mode/dark-mode.service";
import { AuthApiService } from "../shared/services/auth-api/auth-api.service";

@Component({
  selector: "app-layout",
  templateUrl: "./layout.component.html",
  styleUrls: ["./layout.component.scss"],
})
export class LayoutComponent {
  _mobileQueryListener: () => void;
  mobileQuery: MediaQueryList;
  username: string = "";
  firstName: string = "";
  lastName: string = "";

  constructor(
    public router: Router,
    changeDetectorRef: ChangeDetectorRef,
    media: MediaMatcher,
    public darkModeService: DarkModeService
  ) {
    this.mobileQuery = media.matchMedia("(max-width: 600px)");
    this._mobileQueryListener = () => changeDetectorRef.detectChanges();
    this.mobileQuery.addEventListener("change", this._mobileQueryListener);
  }

  ngOnInit(): void {
    this.username = localStorage.getItem(LOCAL_STORAGE_KEYS.USERNAME) || "";
    this.firstName = localStorage.getItem(LOCAL_STORAGE_KEYS.FIRST_NAME) || "";
    this.lastName = localStorage.getItem(LOCAL_STORAGE_KEYS.LAST_NAME) || "";
    this.darkModeService.initDarkModeSettings();
  }

  ngOnDestroy(): void {
    this.mobileQuery.removeEventListener("change", this._mobileQueryListener);
  }

  logout() {
    AuthApiService.logout();
    document.body.classList.remove("se-dark-theme");
    this.router.navigate(["/login"]);
  }
}
