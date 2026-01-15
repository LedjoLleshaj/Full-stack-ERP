import { Injectable } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "src/environment/environments";
import { Client } from "src/app/models/client.model";

@Injectable({
  providedIn: "root",
})
export class ClientService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getClients(): Observable<Client[]> {
    return this.http.get<Client[]>(`${this.apiUrl}${environment.getClients}`);
  }

  getClientById(id: number): Observable<Client> {
    return this.http.get<Client>(`${this.apiUrl}${environment.getClientById}${id}`);
  }
  addClient(client: Client): Observable<Client> {
    return this.http.post<Client>(`${this.apiUrl}${environment.addClient}`, client);
  }

  getClientSales(clientId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/client-sales/${clientId}`);
  }
}
