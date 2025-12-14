import { useEffect, useState } from "react";
import { walletService } from "../api/walletService";
import {
  MOCK_ETH_USD_RATE,
  MOCK_ETH_USD_REFRESH_MS,
  MOCK_ETH_USD_VOLATILITY,
} from "../config";

export function useWallet() {
  const [balance, setBalance] = useState(0);
  const [accountId, setAccountId] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [ethUsdRate, setEthUsdRate] = useState(MOCK_ETH_USD_RATE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const formatError = (e) => {
    if (e?.message && !e.response) return e.message;
    const detail = e?.response?.data?.detail;
    if (!detail) return "Something went wrong";
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      const first = detail[0];
      if (first?.msg) return first.msg;
      if (first?.detail) return first.detail;
    }
    if (typeof detail === "object") return detail.message || JSON.stringify(detail);
    return "Something went wrong";
  };

  const setupAccount = async (publicKey) => {
    setLoading(true);
    setError(null);
    try {
      const data = await walletService.setupAccount(publicKey);
      setBalance(data.balance ?? balance);
      setAccountId(data.account_id ?? accountId);
      return true;
    } catch (e) {
      setError(e.response?.data?.detail || "Account setup failed");
      return false;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const updateRate = () => {
      setEthUsdRate((prev) => {
        const base = MOCK_ETH_USD_RATE;
        const drift = (Math.random() - 0.5) * 2 * MOCK_ETH_USD_VOLATILITY;
        const next = Math.max(100, (prev || base) * (1 + drift));
        return Number(next.toFixed(2));
      });
    };

    const interval = setInterval(updateRate, MOCK_ETH_USD_REFRESH_MS);
    return () => clearInterval(interval);
  }, []);

  const loadAccount = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    setError(null);
    try {
      const data = await walletService.getAccount();
      setBalance(data.balance ?? 0);
      setAccountId(data.account_id ?? null);
    } catch (e) {
      setError(formatError(e));
    }
  };

  const loadTransactions = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    setError(null);
    try {
      const data = await walletService.getTransactions();
      const snapshotRate = ethUsdRate || MOCK_ETH_USD_RATE;
      const txs = Array.isArray(data.transactions) ? data.transactions : [];
      const mapped = txs.map((tx) => {
        const rateUsed = tx.usd_rate_used ?? snapshotRate;
        const usdValue =
          tx.usd_value ??
          Number(((tx.value_eth || 0) * rateUsed).toFixed(2));
        return {
          ...tx,
          usd_rate_used: rateUsed,
          usd_value: usdValue,
        };
      });
      setTransactions(mapped);
    } catch (e) {
      setError(formatError(e));
    }
  };

  const transfer = async ({ toAccount, amount, recipientUsername }) => {
    setLoading(true);
    setError(null);
    try {
      const parsedAccount = Number.parseInt(toAccount, 10);
      const parsedAmount = Number.parseFloat(amount);
      if (!Number.isFinite(parsedAccount) || parsedAccount <= 0) {
        throw new Error("Recipient account ID must be a positive number");
      }
      if (!Number.isFinite(parsedAmount) || parsedAmount <= 0) {
        throw new Error("Amount must be a positive number");
      }
      if (!recipientUsername || !recipientUsername.trim()) {
        throw new Error("Recipient username is required");
      }
      await walletService.transferEth({
        toAccount: parsedAccount,
        amount: parsedAmount,
        recipientUsername: recipientUsername.trim(),
      });
      setBalance((prev) => Math.max(0, prev - parsedAmount));
      await loadTransactions();
      return true;
    } catch (e) {
      setError(formatError(e));
      return false;
    } finally {
      setLoading(false);
    }
  };

  const resetWallet = () => {
    setBalance(0);
    setAccountId(null);
    setTransactions([]);
    setError(null);
    setEthUsdRate(MOCK_ETH_USD_RATE);
  };

  useEffect(() => {
    loadAccount();
    loadTransactions();
  }, []);

  return {
    balance,
    accountId,
    transactions,
    ethUsdRate,
    loading,
    error,
    setupAccount,
    transfer,
    resetWallet,
    loadAccount,
    loadTransactions,
  };
}
