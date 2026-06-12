import { ComponentFixture, TestBed } from "@angular/core/testing";
import { NO_ERRORS_SCHEMA } from "@angular/core";
import { of } from "rxjs";

import { AlertsViewComponent } from "./alerts-view.component";
import { InventoryService } from "src/app/shared/services/inventory-api/inventory.service";
import { ClientService } from "src/app/shared/services/clients-api/client.service";
import { LowStockProduct } from "src/app/models/low-stock.model";

describe("AlertsViewComponent", () => {
  let fixture: ComponentFixture<AlertsViewComponent>;
  let component: AlertsViewComponent;

  const lowStock: LowStockProduct[] = [
    {
      id: 1,
      name: "Flour",
      category: "Food",
      price: 10,
      quantity: 2,
      reorder_level: 5,
      reorder_quantity: 20,
    },
  ];

  const inventoryServiceMock = {
    getLowStock: jasmine.createSpy("getLowStock").and.returnValue(of(lowStock)),
  };
  const clientServiceMock = {
    getClients: jasmine.createSpy("getClients").and.returnValue(of([])),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AlertsViewComponent],
      providers: [
        { provide: InventoryService, useValue: inventoryServiceMock },
        { provide: ClientService, useValue: clientServiceMock },
      ],
      schemas: [NO_ERRORS_SCHEMA],
    }).compileComponents();

    fixture = TestBed.createComponent(AlertsViewComponent);
    component = fixture.componentInstance;
  });

  it("loads low-stock products from the low-stock endpoint", () => {
    fixture.detectChanges();

    expect(inventoryServiceMock.getLowStock).toHaveBeenCalled();
    expect(component.lowStockProducts).toEqual(lowStock);
  });
});
