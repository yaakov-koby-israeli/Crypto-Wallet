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

// Mock ETH/USD settings (tunable)
export const MOCK_ETH_USD_RATE = 2000; // base rate
export const MOCK_ETH_USD_VOLATILITY = 0.01; // +/-1% drift per tick
export const MOCK_ETH_USD_REFRESH_MS = 5000; // update cadence in ms
