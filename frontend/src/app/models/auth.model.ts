export interface LoginResponse {
  user_id: number;
  first_name: string;
  last_name: string;
  username: string;
}

export interface RefreshToken {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  login: LoginResponse;
}

export interface AuthForm {
  username: string;
  password: string;
}
