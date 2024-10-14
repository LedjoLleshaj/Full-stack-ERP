import { Component } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
})
export class AppComponent {
  zoomPercentage = 100;

  zoom(direction: number) {
    const className = document.body.className.replace(
      ` se-zoom-${this.zoomPercentage}`,
      ""
    );
    this.zoomPercentage += direction;
    document.body.className = className + ` se-zoom-${this.zoomPercentage}`;
  }
}
