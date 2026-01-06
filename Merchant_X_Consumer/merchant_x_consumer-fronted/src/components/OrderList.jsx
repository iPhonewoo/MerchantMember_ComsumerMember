import { useEffect, useState } from "react";
import client from "../api/client";

export default function OrderListPage({ onSelect }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get("/store/orders/").then((res) => {
      setOrders(res.data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <p>載入訂單中...</p>;
  }

  return (
    <div>
      <h2>我的訂單</h2>

      {orders.length === 0 && <p>目前沒有訂單</p>}

      {orders.map((order) => (
        <div
          key={order.order_number}
          style={{ border: "1px solid #ccc", margin: 10 }}
        >
          <p>訂單編號：{order.order_number}</p>
          <p>狀態：{order.status}</p>
          <p>金額：{order.total_amount}</p>

          <button onClick={() => onSelect(order.order_number)}>
            查看詳情
          </button>
        </div>
      ))}
    </div>
  );
}
