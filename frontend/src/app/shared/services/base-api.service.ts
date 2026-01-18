import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from 'src/environments/environment';

/**
 * Abstract base class for API services.
 * Provides shared apiUrl and helper methods for consistent HTTP operations.
 */
export abstract class BaseApiService {
  protected apiUrl = environment.apiUrl;

  constructor(protected http: HttpClient) {}

  /**
   * Creates HttpParams from an object, filtering out undefined/null values.
   * @param params - Object with key-value pairs for query parameters
   * @returns HttpParams instance
   */
  protected createParams(params: Record<string, string | number | boolean | undefined | null>): HttpParams {
    let httpParams = new HttpParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        httpParams = httpParams.set(key, String(value));
      }
    });
    return httpParams;
  }
}
