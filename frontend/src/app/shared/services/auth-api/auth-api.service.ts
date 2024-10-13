import { Injectable } from "@angular/core";
import { Subject } from "rxjs";

import { LOCAL_STORAGE_KEYS } from "../../constants";
import { Router } from "@angular/router";
import { Token } from "@angular/compiler";

@Injectable({
  providedIn: "root",
})
export class AuthApiService {
  constructor() {}

  login(username: string, password: string) {
    return new Subject<Token>();
  }

  static logout() {
    Object.values(LOCAL_STORAGE_KEYS).forEach((key) => {
      if (key !== LOCAL_STORAGE_KEYS.DARK_MODE) {
        localStorage.removeItem(key);
      }
    });
    window.location.reload();
  }
}
