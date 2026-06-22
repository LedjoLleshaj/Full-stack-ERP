import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ExpenseApiService } from './expense-api.service';

describe('ExpenseApiService', () => {
  let service: ExpenseApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ExpenseApiService],
    });
    service = TestBed.inject(ExpenseApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('list() unwraps paginated results', () => {
    let result: any;
    service.list().subscribe((r) => (result = r));
    const req = httpMock.expectOne((r) => r.url.endsWith('/api/v1/recurring-expenses/'));
    expect(req.request.method).toBe('GET');
    req.flush({ results: [{ id: 1, name: 'Rent' }], count: 1 });
    expect(result.length).toBe(1);
    expect(result[0].name).toBe('Rent');
  });

  it('charge() posts to the charge action', () => {
    service.charge(7).subscribe();
    const req = httpMock.expectOne((r) => r.url.endsWith('/api/v1/recurring-expenses/7/charge/'));
    expect(req.request.method).toBe('POST');
    req.flush({ id: 99 });
  });

  it('runDue() posts to run-due', () => {
    service.runDue().subscribe();
    const req = httpMock.expectOne((r) => r.url.endsWith('/api/v1/recurring-expenses/run-due/'));
    expect(req.request.method).toBe('POST');
    req.flush({ charged: 2, total_amount: '40.00' });
  });
});
