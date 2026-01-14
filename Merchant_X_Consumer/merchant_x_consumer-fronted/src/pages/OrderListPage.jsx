import { useEffect, useState } from "react";
import client from "../api/client";

export default function OrderListPage() {
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const res = await client.get("/store/orders/");
        setOrders(res.data.results);
      } catch (err) {
        setError("無法取得訂單列表");
      }
    };

    fetchOrders();
  }, []);

  if (error) {
    return <p style={{ color: "red" }}>{error}</p>;
  }

  return (
    <div>
      <h1>我的訂單</h1>

      {orders.length === 0 && <p>目前沒有訂單</p>}

      {orders.map(order => (
        <div
          key={order.id}
          style={{ border: "1px solid #ccc", marginBottom: "12px", padding: "8px" }}
        >
          <p>訂單編號：{order.id}</p>
          <p>收件人：{order.receiver_name}</p>
          <p>下單時間：{order.created_at}</p>

          <ul>
            {order.items.map((item, idx) => (
              <li key={idx}>
                {item.product_name} × {item.quantity}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

