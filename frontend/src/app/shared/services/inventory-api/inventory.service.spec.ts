import { TestBed } from "@angular/core/testing";
import { HttpClientTestingModule, HttpTestingController } from "@angular/common/http/testing";

import { InventoryService } from "./inventory.service";
import { LowStockProduct } from "src/app/models/low-stock.model";

describe("InventoryService", () => {
  let service: InventoryService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
    });
    service = TestBed.inject(InventoryService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it("getLowStock calls v1 low-stock endpoint and returns products", () => {
    const mockResponse: LowStockProduct[] = [
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

    let result: LowStockProduct[] | undefined;
    service.getLowStock().subscribe((data) => (result = data));

    const req = httpMock.expectOne("http://localhost:8080/api/v1/inventory/low-stock/");
    expect(req.request.method).toBe("GET");
    req.flush(mockResponse);

    expect(result).toEqual(mockResponse);
  });
});
