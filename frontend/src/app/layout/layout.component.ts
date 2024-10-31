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
  isProductMenuOpen: boolean = false; // Track product menu state
  isRightNavOpen: boolean = false; // Track right nav state
  cartItems: any[] = []; // Store unique cart items with their counts

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
    this.loadCartItems();
  }

  ngOnDestroy(): void {
    this.mobileQuery.removeEventListener("change", this._mobileQueryListener);
  }

  logout() {
    AuthApiService.logout();
    document.body.classList.remove("se-dark-theme");
    this.router.navigate(["/login"]);
  }

  navigateToProducts() {
    this.isProductMenuOpen = !this.isProductMenuOpen;
    this.router.navigate(['/products']);
  }

  // Shopping cart menu open-close function
  toggleRightNav() {
    this.isRightNavOpen = !this.isRightNavOpen;
  }

  // TODO:
  loadCartItems() {
    const storedItems = JSON.parse(localStorage.getItem('cartItems') || '[]');
    const itemCounts: { [key: string]: { count: number; item: any } } = {};

    storedItems.forEach((item: any) => {
      if (itemCounts[item.id]) {
        itemCounts[item.id].count++;
      } else {
        itemCounts[item.id] = { count: 1, item };
      }
    });

    this.cartItems = Object.values(itemCounts).map(entry => ({
      ...entry.item,
      count: entry.count,
    }));
  }
}
