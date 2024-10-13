import { Injectable } from "@angular/core";
import { LOCAL_STORAGE_KEYS } from "../../constants";

@Injectable({
  providedIn: "root",
})
export class DarkModeService {
  public darkMode: boolean = false;

  initDarkModeSettings(): void {
    this.loadDarkModeSetting();
    this.applyDarkMode();
  }

  toggleDarkMode(): void {
    this.darkMode = !this.darkMode;
    localStorage.setItem(
      LOCAL_STORAGE_KEYS.DARK_MODE,
      this.darkMode.toString()
    );
    this.applyDarkMode();
  }

  private loadDarkModeSetting(): void {
    this.darkMode =
      localStorage.getItem(LOCAL_STORAGE_KEYS.DARK_MODE) === "true";
  }

  private applyDarkMode(): void {
    this.darkMode
      ? document.body.classList.add("se-dark-theme")
      : document.body.classList.remove("se-dark-theme");
  }
}
