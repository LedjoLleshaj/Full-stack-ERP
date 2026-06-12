import { TestBed, ComponentFixture } from "@angular/core/testing";
import { NO_ERRORS_SCHEMA } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";
import { of } from "rxjs";

import { ProductDetailsViewComponent } from "./product-details-view.component";
import { ProductService, ProductHistory } from "../../../../shared/services/product-api/product.service";
import { DarkModeService } from "../../../../shared/services/dark-mode/dark-mode.service";
import { CurrencyExchangeService } from "../../../../shared/services/currency-exchange/currency-exchange.service";
import { AuthApiService } from "src/app/shared/services/auth-api/auth-api.service";

describe("ProductDetailsViewComponent", () => {
  let fixture: ComponentFixture<ProductDetailsViewComponent>;
  let component: ProductDetailsViewComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ProductDetailsViewComponent],
      providers: [
        { provide: ActivatedRoute, useValue: { snapshot: { paramMap: { get: () => "1" } } } },
        { provide: Router, useValue: { navigate: () => {} } },
        { provide: ProductService, useValue: {} },
        { provide: DarkModeService, useValue: { darkMode$: of(false) } },
        { provide: CurrencyExchangeService, useValue: { getExchangeRates: () => of({ rates: {} }) } },
        { provide: MatSnackBar, useValue: { open: () => {} } },
        { provide: AuthApiService, useValue: {} },
      ],
      schemas: [NO_ERRORS_SCHEMA],
    }).compileComponents();

    fixture = TestBed.createComponent(ProductDetailsViewComponent);
    component = fixture.componentInstance;
  });

  it("toggleEdit copies reorder settings into the edit form", () => {
    component.productHistory = {
      product: {
        id: 1,
        name: "Flour",
        category: "Food",
        price: 10,
        description: "d",
        disponibility: 2,
        reorder_level: 5,
        reorder_quantity: 20,
      },
    } as ProductHistory;

    component.toggleEdit();

    expect(component.editForm.reorder_level).toBe(5);
    expect(component.editForm.reorder_quantity).toBe(20);
  });
});
