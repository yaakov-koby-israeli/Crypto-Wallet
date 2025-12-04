export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const ENDPOINTS = {
  login: "/auth/token",
  register: "/auth",
  setupAccount: "/user/set-up-account",
  account: "/user/account",
  transferEth: "/user/transfer-eth",
  transactions: "/user/user-transactions",
};