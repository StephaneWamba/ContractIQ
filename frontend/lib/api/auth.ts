/**
 * Authentication API client
 */
import { fetchApi } from "./client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
}

export const authApi = {
  login: (data: LoginRequest) =>
    fetchApi<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  
  register: (data: RegisterRequest) =>
    fetchApi<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  
  getMe: () =>
    fetchApi<User>("/auth/me"),
};

