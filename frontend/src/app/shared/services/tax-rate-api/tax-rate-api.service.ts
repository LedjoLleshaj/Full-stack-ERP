import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { TaxRate } from '../../../models/tax-rate.model';
import { BaseApiService } from '../base-api.service';

@Injectable({
  providedIn: 'root',
})
export class TaxRateApiService extends BaseApiService {
  constructor(http: HttpClient) {
    super(http);
  }

  getTaxRates(): Observable<TaxRate[]> {
    return this.http
      .get<{ results: TaxRate[] }>(`${this.apiV1Url}/tax-rates/`)
      .pipe(map((response) => response.results));
  }
}
