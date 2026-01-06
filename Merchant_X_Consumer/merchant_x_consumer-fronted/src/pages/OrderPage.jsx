import { useState } from "react";
import client from "../api/client";

export default function OrderPage({ productId, onDone }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const createOrder = async () => {
    setLoading(true);
    setError("");

    try {
      await client.post("/store/orders/", {
        receiver_name: "王小明",
        receiver_phone: "0912345678",
        address: "台北市信義區",
        items: [
          {
            product: productId,
            quantity: 1,
          },
        ],
      });

      onDone();
    } catch (err) {
      setError("下單失敗，可能是庫存不足");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>建立訂單</h2>

      <button onClick={createOrder} disabled={loading}>
        {loading ? "送出中..." : "確認下單"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
