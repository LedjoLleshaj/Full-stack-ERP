import { TestBed } from "@angular/core/testing";
import { HttpClientTestingModule, HttpTestingController } from "@angular/common/http/testing";

import { TaxRateApiService } from "./tax-rate-api.service";
import { TaxRate } from "../../../models/tax-rate.model";

describe("TaxRateApiService", () => {
  let service: TaxRateApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
    });
    service = TestBed.inject(TaxRateApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it("getTaxRates calls v1 tax-rates endpoint (not under /erp) and unwraps results", () => {
    const mockRates: TaxRate[] = [
      { id: 1, name: "Standard", rate: "20.00", is_default: true, is_active: true },
    ];

    let result: TaxRate[] | undefined;
    service.getTaxRates().subscribe((data) => (result = data));

    const req = httpMock.expectOne("http://localhost:8080/api/v1/tax-rates/");
    expect(req.request.method).toBe("GET");
    req.flush({ results: mockRates });

    expect(result).toEqual(mockRates);
  });
});
