import { MediaMatcher } from "@angular/cdk/layout";
import { ChangeDetectorRef, Component, ViewChild } from "@angular/core";
import { Router } from "@angular/router";
import { LOCAL_STORAGE_KEYS } from "../core";
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
  isClientMenuOpen: boolean = false; // Track client menu state
  isSupplierMenuOpen: boolean = false; // Track supplier menu state
  isSaleMenuOpen: boolean = false; // Track sale menu state
  isRestockMenuOpen: boolean = false; // Track restock menu state

  constructor(
    public router: Router,
    changeDetectorRef: ChangeDetectorRef,
    media: MediaMatcher,
    public authApiService: AuthApiService,
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
  }

  ngOnDestroy(): void {
    this.mobileQuery.removeEventListener("change", this._mobileQueryListener);
  }

  logout() {
    this.authApiService.logout();
    this.router.navigate(["/login"]);
  }

  navigateToProducts() {
    this.router.navigate(["/products"]);
  }
  navigateToClients() {
    this.isClientMenuOpen = !this.isClientMenuOpen;
    this.router.navigate(["/clients"]);
  }
  navigateToSuppliers() {
    this.isSupplierMenuOpen = !this.isSupplierMenuOpen;
    this.router.navigate(["/suppliers"]);
  }
  navigateToSales() {
    this.isSaleMenuOpen = !this.isSaleMenuOpen;
    this.router.navigate(["/sales"]);
  }


  navigateToRestocks() {
    this.isRestockMenuOpen = !this.isRestockMenuOpen;
    this.router.navigate(["/restocks"]);
  }

}
