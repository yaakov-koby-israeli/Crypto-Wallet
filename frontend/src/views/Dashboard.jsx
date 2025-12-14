import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Input, Logo } from "../components/ui/Components";
import { MOCK_ETH_USD_RATE } from "../config";

// Simple conversion helper; rate is supplied so it can change over time
const toDollars = (eth, rate) => {
  const value = Number(eth) || 0;
  const usdRate = rate || MOCK_ETH_USD_RATE;
  return (value * usdRate).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const formatUsd = (usd) =>
  Number(usd || 0).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

export const Dashboard = ({
  user,
  balance,
  accountId,
  transactions,
  ethUsdRate,
  onLogout,
  onSetup,
  onTransfer,
  onRefreshAccount,
  onRefreshTransactions,
  loading,
  error,
}) => {
  const navigate = useNavigate();
  const [publicKey, setPublicKey] = useState(user?.public_key || "");
  const [transfer, setTransfer] = useState({ toAccount: "", username: "", amount: "" });
  const [transferErrors, setTransferErrors] = useState({});
  const [transferStatus, setTransferStatus] = useState(null);

  useEffect(() => {
    setPublicKey(user?.public_key || "");
  }, [user?.public_key]);

  useEffect(() => {
    if (!user?.id) return;
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${protocol}://localhost:8000/user/ws/${user.id}`);

    ws.onmessage = async (event) => {
      if (event.data === "update_balance") {
        if (onRefreshAccount) await onRefreshAccount();
        if (onRefreshTransactions) await onRefreshTransactions();
      }
    };

    return () => ws.close();
  }, [user?.id, onRefreshAccount, onRefreshTransactions]);

  const validateTransfer = () => {
    const errs = {};
    const toAccountNum = Number(transfer.toAccount);
    const amountNum = Number(transfer.amount);
    if (!transfer.username.trim()) {
      errs.username = "Recipient username is required";
    }
    if (!transfer.toAccount.trim() || Number.isNaN(toAccountNum) || toAccountNum <= 0) {
      errs.toAccount = "Recipient account ID must be a positive number";
    }
    if (!transfer.amount.trim() || Number.isNaN(amountNum) || amountNum <= 0) {
      errs.amount = "Amount must be a positive number";
    }
    setTransferErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const setup = (e) => {
    e.preventDefault();
    onSetup(publicKey);
  };

  const send = async (e) => {
    e.preventDefault();
    if (!validateTransfer()) return;
    setTransferStatus(null);
    const ok = await onTransfer({
      toAccount: Number(transfer.toAccount),
      amount: Number(transfer.amount),
      recipientUsername: transfer.username,
    });
    if (ok) {
      setTransferErrors({});
      setTransfer({ toAccount: "", username: "", amount: "" });
      setTransferStatus("Transfer submitted");
    } else {
      setTransferStatus("Transfer failed. Please check the details and try again.");
    }
  };

  const isKeyLinked = !!user?.public_key;
  const sortedTxs = useMemo(() => {
    if (!Array.isArray(transactions)) return [];
    return [...transactions].sort((a, b) => {
      const blockDiff = (b.block_number || 0) - (a.block_number || 0);
      if (blockDiff !== 0) return blockDiff;
      return (b.nonce || 0) - (a.nonce || 0);
    });
  }, [transactions]);

  const handleLogoutClick = () => {
    if (onLogout) onLogout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-screen bg-surface-dark text-white">
      <header className="flex items-center justify-between px-6 py-4 border-b border-white/5">
        <div className="flex items-center gap-4">
          <Logo />
          <span className="text-sm text-white/60">| Welcome, {user?.username}</span>
        </div>
        <Button variant="ghost" onClick={handleLogoutClick}>
          Sign Out
        </Button>
      </header>

      <main className="px-6 pb-12 space-y-8 animate-fade-slide mt-6">
        <section className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/0 p-6 shadow-soft">
          <div className="text-sm uppercase tracking-wide text-white/50">Total Balance</div>
          <div className="flex items-baseline gap-3 mt-3">
            <span className="text-5xl font-semibold">{balance?.toFixed?.(4) || "0.0000"} ETH</span>
            <span className="text-xl text-white/40">{toDollars(balance || 0, ethUsdRate)}</span>
          </div>
          {accountId && (
            <div className="mt-2 text-sm text-white/60">
              Account ID: <span className="text-accent">{accountId}</span>
            </div>
          )}
          {error && (
            <div className="mt-2 text-sm text-red-400 bg-red-400/10 p-2 rounded">{error}</div>
          )}
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-1 rounded-2xl border border-white/10 bg-white/5 p-5 shadow-soft h-fit">
            <div className="text-lg font-semibold">Account Status</div>
            <p className="text-sm text-white/60 mb-4">
              {isKeyLinked
                ? "Your public key is validated and active."
                : "Link your Ganache public key to sync balance."}
            </p>

            {isKeyLinked ? (
              <div className="space-y-2">
                <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm">
                  <div className="font-semibold mb-1">Validated Public Key</div>
                  <div className="break-all font-mono text-xs opacity-80">{user.public_key}</div>
                </div>
                <Input label="Status" value="Validated" readOnly disabled />
              </div>
            ) : (
              <form className="space-y-3" onSubmit={setup}>
                <Input
                  label="Public Key"
                  value={publicKey}
                  onChange={(e) => setPublicKey(e.target.value)}
                  placeholder="0x..."
                />
                <Button type="submit" loading={loading} className="w-full">
                  Sync Account
                </Button>
              </form>
            )}
          </div>

          <div className="lg:col-span-2 rounded-2xl border border-white/10 bg-white/5 p-5 shadow-soft space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-lg font-semibold">Transfer ETH</div>
            </div>
            <form className="grid gap-4 md:grid-cols-2" onSubmit={send} noValidate>
              <div className="col-span-1">
                <Input
                  label="Recipient Username"
                  value={transfer.username}
                  onChange={(e) => setTransfer({ ...transfer, username: e.target.value })}
                  placeholder="e.g. user2"
                />
                {transferErrors.username && (
                  <div className="mt-1 text-xs text-red-400">{transferErrors.username}</div>
                )}
              </div>
              <div className="col-span-1">
                <Input
                  label="Recipient Account ID"
                  value={transfer.toAccount}
                  onChange={(e) => setTransfer({ ...transfer, toAccount: e.target.value })}
                  placeholder="e.g. 1"
                />
                {transferErrors.toAccount && (
                  <div className="mt-1 text-xs text-red-400">{transferErrors.toAccount}</div>
                )}
              </div>
              <div className="col-span-2 md:col-span-1">
                <Input
                  label="Amount (ETH)"
                  value={transfer.amount}
                  onChange={(e) => setTransfer({ ...transfer, amount: e.target.value })}
                  placeholder="0.1"
                />
                {transferErrors.amount && (
                  <div className="mt-1 text-xs text-red-400">{transferErrors.amount}</div>
                )}
              </div>
              <div className="col-span-2 md:col-span-1 flex items-end">
                <Button type="submit" loading={loading} className="w-full">
                  Send Funds
                </Button>
              </div>
              {transferStatus && (
                <div className="col-span-2 text-sm text-white/70">{transferStatus}</div>
              )}
              {error && (
                <div className="col-span-2 text-sm text-red-400 bg-red-400/10 p-2 rounded">
                  {error}
                </div>
              )}
            </form>
          </div>
        </section>

        <section className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-soft">
          <div className="text-lg font-semibold mb-4">Recent Activity</div>
          <div className="space-y-3">
            {sortedTxs.length === 0 && (
              <div className="text-sm text-white/50 text-center py-4">No transactions found.</div>
            )}
            {sortedTxs.map((tx) => {
              const toAddr = tx.to || "";
              const isIncoming =
                toAddr.toLowerCase() === (user?.public_key || "").toLowerCase();
              const colorClass = isIncoming ? "text-green-400" : "text-red-400";
              const badgeClass = isIncoming
                ? "bg-green-500/15 text-green-200"
                : "bg-red-500/15 text-red-200";
              const sign = isIncoming ? "+" : "-";
              const fromDisplay = tx.from_username || tx.from || "External";
              const toDisplay = tx.to_username || tx.to || "External";
              const usdValue =
                tx.usd_value ??
                Number(
                  ((tx.value_eth || 0) * (tx.usd_rate_used ?? ethUsdRate)).toFixed(2)
                );

              return (
                <div
                  key={tx.hash}
                  className="flex items-center justify-between rounded-xl border border-white/5 bg-surface-dim/40 px-4 py-4 hover:bg-surface-dim/60 transition"
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center bg-white/5 ${colorClass}`}
                    >
                      {isIncoming ? "IN" : "OUT"}
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white/90 flex items-center gap-2">
                        {isIncoming ? "Received from" : "Sent to"}
                        <span className="opacity-60 ml-1 font-mono text-xs">
                          {isIncoming ? fromDisplay : toDisplay}
                        </span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full ${badgeClass}`}>
                          Block #{tx.block_number}
                        </span>
                      </div>
                      <div className="text-xs text-white/40 mt-0.5">
                        Hash: {tx.hash.substring(0, 16)}...
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className={`text-lg font-bold ${colorClass}`}>
                      {sign} {tx.value_eth?.toFixed?.(4) ?? tx.value_eth} ETH
                    </div>
                    <div className="text-xs text-white/60">
                      {sign} {formatUsd(usdValue)}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </main>
    </div>
  );
};
