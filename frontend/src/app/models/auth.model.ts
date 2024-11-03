export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  login: LoginResponse;
}

export interface AuthForm {
  username: string;
  password: string;
}
