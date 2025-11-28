import { Component, OnInit, OnDestroy, Renderer2 } from "@angular/core";
import { DarkModeService } from "./shared/services/dark-mode/dark-mode.service";
import { Subscription } from "rxjs";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
})
export class AppComponent implements OnInit, OnDestroy {
  private darkModeSubscription: Subscription | undefined;

  constructor(
    private darkModeService: DarkModeService,
    private renderer: Renderer2
  ) {}

  ngOnInit(): void {
    this.darkModeSubscription = this.darkModeService.darkMode$.subscribe(
      (isDark) => {
        if (isDark) {
          this.renderer.addClass(document.body, "dark-mode");
        } else {
          this.renderer.removeClass(document.body, "dark-mode");
        }
      }
    );
  }

  ngOnDestroy(): void {
    this.darkModeSubscription?.unsubscribe();
  }
}
