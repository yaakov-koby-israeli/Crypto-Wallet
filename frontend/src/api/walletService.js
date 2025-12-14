import axios from "axios";
import { API_BASE_URL, ENDPOINTS } from "../config";

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const walletService = {
  login: async ({ username, password }) => {
    const data = new URLSearchParams();
    data.append("username", username);
    data.append("password", password);
    const res = await api.post(ENDPOINTS.login, data, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return res.data;
  },

  register: async (payload) => {
    const res = await api.post(ENDPOINTS.register, payload);
    return res.data;
  },

  setupAccount: async (publicKey) => {
    const res = await api.post(
      ENDPOINTS.setupAccount,
      {},
      { params: { public_key: publicKey } }
    );
    return res.data;
  },

  getAccount: async () => {
    const res = await api.get(ENDPOINTS.account);
    return res.data;
  },

  transferEth: async ({ recipientUsername, toAccount, amount }) => {
    const payload = {
      recipient_username: recipientUsername,
      to_account: Number.parseInt(toAccount, 10),
      amount: Number.parseFloat(amount),
    };
    const res = await api.post(ENDPOINTS.transferEth, payload, {
      headers: { "Content-Type": "application/json" },
    });
    return res.data;
  },

  getTransactions: async () => {
    const res = await api.get(ENDPOINTS.transactions);
    return res.data;
  },
};

export default walletService;
