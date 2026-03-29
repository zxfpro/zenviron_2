export type ErrorResponse = {
  detail: string;
};

export type SendEmailCodeRequest = {
  email: string;
};

export type RegisterWithCodeRequest = {
  email: string;
  code: string;
  password: string;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
};

export type ForgotPasswordRequest = {
  email: string;
};

export type ResetPasswordRequest = {
  email: string;
  code: string;
  new_password: string;
};

export type PhoneCodeRequest = {
  phone: string;
};

export type PhoneLoginRequest = {
  phone: string;
  code: string;
};

export type UserMeResponse = {
  id: string;
  email: string | null;
  phone: string | null;
  is_active: boolean;
};
