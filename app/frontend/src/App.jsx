import React, { useState } from "react";
import { fetchData } from "./services/api";

function App() {
  const [symbol, setSymbol] = useState("BTC-USD");
  const [msg, setMsg] = useState("");

  const handleFetch = async () => {
    const res = await fetchData(symbol);
    setMsg(res?.message || "Error fetching data");
  };

  return (
    <div style={{ textAlign: "center", padding: "2rem" }}>
      <h1>Financial Data Loader</h1>
      <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
        <option value="BTC-USD">BTC-USD</option>
        <option value="AAPL">AAPL</option>
        <option value="EURUSD=X">EUR/USD</option>
      </select>
      <button onClick={handleFetch} style={{ marginLeft: "1rem" }}>
        Fetch & Store
      </button>
      <p>{msg}</p>
    </div>
  );
}

export default App;
