import { Component } from "@angular/core";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
})
export class AppComponent {
  zoomPercentage = 100;

  zoom(direction: number) {
    const className = document.body.className.replace(
      ` rf-zoom-${this.zoomPercentage}`,
      ""
    );
    this.zoomPercentage += direction;
    document.body.className = className + ` rf-zoom-${this.zoomPercentage}`;
  }
}
