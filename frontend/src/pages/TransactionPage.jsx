import React, { useEffect, useState } from "react";
import api from "../api";

const TransactionPage = () => {
  const [user, setUser] = useState(null);
  const [wallets, setWallets] = useState([]);
  const [users, setUsers] = useState([]);
  const [receiverId, setReceiverId] = useState("");
  const [senderWalletId, setSenderWalletId] = useState("");
  const [receiverWalletId, setReceiverWalletId] = useState("");
  const [amount, setAmount] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [receiverWallets, setReceiverWallets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currencies, setCurrencies] = useState([]);
  const [newWalletBalance, setNewWalletBalance] = useState("");
  const [newWalletCurrency, setNewWalletCurrency] = useState("");

  // ===== Fetch initial data =====
  useEffect(() => {
    fetchUser();
    fetchWallets();
    fetchUsers();
    fetchCurrencies();
  }, []);

  const fetchUser = () => {
    api.get("/api/profile/")
      .then(res => setUser(res.data))
      .catch(() => alert("Failed to fetch user"));
  };

  const fetchWallets = () => {
    api.get("/finance/wallets/")
      .then(res => {
        setWallets(res.data);
        if (res.data.length) setSenderWalletId(res.data[0].id);
      })
      .catch(() => alert("Failed to fetch wallets"));
  };

  const fetchUsers = () => {
    api.get("/finance/users/")
      .then(res => setUsers(res.data))
      .catch(() => alert("Failed to fetch users"));
  };

  const fetchCurrencies = () => {
    api.get("/finance/currencies/")
      .then(res => {
        setCurrencies(res.data);
        if (res.data.length) setNewWalletCurrency(res.data[0].code);
      })
      .catch(() => alert("Failed to fetch currencies"));
  };

  // ===== Handle wallet creation =====
  const handleCreateWallet = () => {
    if (!newWalletBalance || !newWalletCurrency) {
      alert("Enter balance and currency");
      return;
    }
    api.post("/finance/create-wallet/", {
      balance: newWalletBalance,
      currency: newWalletCurrency
    })
    .then(() => {
      alert("Wallet created!");
      setNewWalletBalance("");
      setNewWalletCurrency(currencies[0]?.code || "");
      fetchWallets();
    })
    .catch(err => alert(err.response?.data?.detail || "Failed to create wallet"));
  };

  // ===== Handle transaction =====
  const handleTransaction = () => {
    if (!senderWalletId || !receiverWalletId || !amount || !totpCode || !receiverId) {
      alert("Fill all fields");
      return;
    }

    const senderWallet = wallets.find(w => w.id === parseInt(senderWalletId));
    const receiverWallet = receiverWallets.find(w => w.id === parseInt(receiverWalletId));

    if (!senderWallet || !receiverWallet) {
      alert("Invalid wallet selection");
      return;
    }

    setLoading(true);

    const payload = {
      sender: senderWallet.user_id,        
      receiver: receiverId,                
      amount: parseFloat(amount),
      sender_currency: senderWallet.currency,
      receiver_currency: receiverWallet.currency,
      totp_code: totpCode
    };

    api.post("/finance/transactions/create/", payload)
      .then(() => {
        alert("Transaction successful!");
        setAmount("");
        setTotpCode("");
        setReceiverId("");
        setReceiverWalletId("");
        fetchWallets();
      })
      .catch(err => alert(err.response?.data?.detail || "Transaction failed"))
      .finally(() => setLoading(false));
  };

  // ===== Update receiver wallets when receiver changes =====
  const handleReceiverChange = (id) => {
    setReceiverId(id);
    if (!id) {
      setReceiverWallets([]);
      setReceiverWalletId("");
      return;
    }
    api.get(`/finance/wallets/by-user/?user_id=${id}`)
      .then(res => {
        setReceiverWallets(res.data);
        if (res.data.length) setReceiverWalletId(res.data[0].id);
      })
      .catch(() => {
        setReceiverWallets([]);
        setReceiverWalletId("");
        alert("Failed to fetch receiver wallets");
      });
  };

  if (!user) return <div>Loading...</div>;

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>Finance Dashboard</h1>
      

      {/* User wallets */}
      <div style={styles.card}>
        <p>{user.username}</p>
        <h2>Your Wallets</h2>
        {wallets.length === 0 ? <p>No wallets</p> : (
          <ul>{wallets.map(w => <li key={w.id}>{w.currency}: {w.balance}</li>)}</ul>
        )}
      </div>

      {/* Create wallet */}
      <div style={styles.card}>
        <h2>Create Wallet</h2>
        <input
          type="number"
          placeholder="Balance"
          value={newWalletBalance}
          onChange={e => setNewWalletBalance(e.target.value)}
          style={styles.input}
        />
        <select
          value={newWalletCurrency}
          onChange={e => setNewWalletCurrency(e.target.value)}
          style={styles.input}
        >
          {currencies.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
        </select>
        <button onClick={handleCreateWallet} style={styles.button}>Create Wallet</button>
      </div>

      {/* Transaction */}
      <div style={styles.card}>
        <h2>Send Money</h2>

        {/* Receiver selection */}
        <select value={receiverId} onChange={e => handleReceiverChange(e.target.value)} style={styles.input}>
          <option value="">Select Receiver</option>
          {users.map(u => <option key={u.id} value={u.id}>{u.username}</option>)}
        </select>

        {/* Sender wallet */}
        <select value={senderWalletId} onChange={e => setSenderWalletId(e.target.value)} style={styles.input}>
          {wallets.map(w => <option key={w.id} value={w.id}>{w.currency}</option>)}
        </select>

        {/* Receiver wallet */}
        {receiverWallets.length > 0 && (
          <select value={receiverWalletId} onChange={e => setReceiverWalletId(e.target.value)} style={styles.input}>
            {receiverWallets.map(w => <option key={w.id} value={w.id}>{w.currency}</option>)}
          </select>
        )}

        <input
          type="number"
          placeholder="Amount"
          value={amount}
          onChange={e => setAmount(e.target.value)}
          style={styles.input}
        />
        <input
          type="text"
          placeholder="2FA Code"
          value={totpCode}
          onChange={e => setTotpCode(e.target.value)}
          style={styles.input}
        />

        <button onClick={handleTransaction} style={styles.button} disabled={loading}>
          {loading ? "Processing..." : "Send"}
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: { maxWidth: "600px", margin: "50px auto", fontFamily: "Arial" },
  heading: { textAlign: "center", marginBottom: "30px", color: "#004d40" },
  card: { border: "1px solid #004d40", borderRadius: "12px", padding: "20px", marginBottom: "20px", backgroundColor: "#e0f7fa" },
  input: { display: "block", width: "100%", padding: "12px", marginBottom: "10px", borderRadius: "6px", border: "1px solid #004d40" },
  button: { padding: "12px 20px", backgroundColor: "#004d40", color: "#fff", border: "none", borderRadius: "6px", cursor: "pointer" }
};

export default TransactionPage;
