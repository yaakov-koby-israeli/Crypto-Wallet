import { useState } from "react";
import { Button, Input, Logo } from "../components/ui/Components";

export const Dashboard = ({
  user,
  balance,
  accountId,
  transactions,
  onSetup,
  onTransfer,
  loading,
  error,
}) => {
  const [publicKey, setPublicKey] = useState(user?.public_key || "");
  const [transfer, setTransfer] = useState({ toAccount: "", amount: "" });

  const setup = (e) => {
    e.preventDefault();
    onSetup(publicKey);
  };

  const send = (e) => {
    e.preventDefault();
    onTransfer(transfer);
    setTransfer({ toAccount: "", amount: "" });
  };

  return (
    <div className="min-h-screen bg-surface-dark text-white">
      <header className="flex items-center justify-between px-6 py-4">
        <Logo />
        <div className="text-sm text-white/60">Hi, {user?.username}</div>
      </header>

      <main className="px-6 pb-12 space-y-8 animate-fade-slide">
        <section className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/0 p-6 shadow-soft">
          <div className="text-sm uppercase tracking-wide text-white/50">Total Balance</div>
          <div className="mt-3 text-5xl font-semibold">${balance?.toFixed?.(4) || "0.0000"}</div>
          {accountId && (
            <div className="mt-2 text-sm text-white/60">Account ID: {accountId}</div>
          )}
          {error && <div className="mt-2 text-sm text-red-400">{error}</div>}
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-1 rounded-2xl border border-white/10 bg-white/5 p-5 shadow-soft">
            <div className="text-lg font-semibold">Setup / Update Account</div>
            <p className="text-sm text-white/60">
              Link your Ganache public key and sync balance.
            </p>
            <form className="mt-4 space-y-3" onSubmit={setup}>
              <Input
                label="Public Key"
                value={publicKey}
                onChange={(e) => setPublicKey(e.target.value)}
                placeholder="0x..."
              />
              <Button type="submit" loading={loading}>
                Sync Account
              </Button>
            </form>
          </div>

          <div className="lg:col-span-2 rounded-2xl border border-white/10 bg-white/5 p-5 shadow-soft space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-lg font-semibold">Transfer ETH</div>
              <div className="text-xs text-white/50">
                Send directly to another account ID.
              </div>
            </div>
            <form className="grid gap-3 md:grid-cols-3" onSubmit={send}>
              <Input
                label="To Account"
                value={transfer.toAccount}
                onChange={(e) => setTransfer({ ...transfer, toAccount: e.target.value })}
                placeholder="Account ID"
              />
              <Input
                label="Amount (ETH)"
                value={transfer.amount}
                onChange={(e) => setTransfer({ ...transfer, amount: e.target.value })}
                placeholder="0.1"
              />
              <div className="flex items-end">
                <Button type="submit" loading={loading}>
                  Send
                </Button>
              </div>
            </form>
          </div>
        </section>

        <section className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-soft">
          <div className="text-lg font-semibold mb-3">Transaction History</div>
          <div className="space-y-3">
            {(transactions || []).length === 0 && (
              <div className="text-sm text-white/50">No transactions yet.</div>
            )}
            {(transactions || []).map((tx) => (
              <div
                key={tx.hash}
                className="flex items-center justify-between rounded-xl border border-white/10 bg-surface-dim/60 px-4 py-3"
              >
                <div>
                  <div className="text-sm font-semibold truncate">{tx.hash}</div>
                  <div className="text-xs text-white/50">
                    {tx.from} → {tx.to || "Contract"}
                  </div>
                </div>
                <div className="text-sm font-semibold text-accent">
                  {tx.value_eth} ETH
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
};
