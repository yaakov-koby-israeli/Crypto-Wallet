import { useEffect, useState } from "react";
import { walletService } from "../api/walletService";

export function useWallet() {
  const [balance, setBalance] = useState(0);
  const [accountId, setAccountId] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const loadTransactions = async () => {
    setError(null);
    try {
      const data = await walletService.getTransactions();
      setTransactions(data.transactions || []);
    } catch (e) {
      setError(e.response?.data?.detail || "Could not load transactions");
    }
  };

  const transfer = async ({ toAccount, amount }) => {
    setLoading(true);
    setError(null);
    try {
      await walletService.transferEth({ toAccount, amount });
      setBalance((prev) => Math.max(0, prev - Number(amount)));
      await loadTransactions();
      return true;
    } catch (e) {
      setError(e.response?.data?.detail || "Transfer failed");
      return false;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, []);

  return {
    balance,
    accountId,
    transactions,
    loading,
    error,
    setupAccount,
    transfer,
    loadTransactions,
  };
}
