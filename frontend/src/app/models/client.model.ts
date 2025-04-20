export interface Client {
  id?: number;
  firstname: string;
  lastname: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  unpaidBalance: number;
  totalBought?: number;
}
