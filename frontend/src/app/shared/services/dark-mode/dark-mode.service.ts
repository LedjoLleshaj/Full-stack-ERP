import { Injectable } from "@angular/core";
import { BehaviorSubject, Observable } from "rxjs";
import { LOCAL_STORAGE_KEYS } from "../../constants";

@Injectable({
  providedIn: "root",
})
export class DarkModeService {
  private darkModeSubject: BehaviorSubject<boolean>;
  public darkMode$: Observable<boolean>;

  constructor() {
    const isDark = localStorage.getItem(LOCAL_STORAGE_KEYS.DARK_MODE) === "true";
    this.darkModeSubject = new BehaviorSubject<boolean>(isDark);
    this.darkMode$ = this.darkModeSubject.asObservable();
  }

  toggleDarkMode(): void {
    const newValue = !this.darkModeSubject.value;
    this.darkModeSubject.next(newValue);
    localStorage.setItem(LOCAL_STORAGE_KEYS.DARK_MODE, newValue.toString());
  }

  isDarkMode(): boolean {
    return this.darkModeSubject.value;
  }

  setDarkMode(enabled: boolean): void {
    this.darkModeSubject.next(enabled);
    localStorage.setItem(LOCAL_STORAGE_KEYS.DARK_MODE, enabled.toString());
  }
}
