import { useEffect, useState } from "react";
import client from "../api/client";

export default function OrderDetailPage({ orderNumber, onBack }) {
  const [order, setOrder] = useState(null);

  useEffect(() => {
    client.get(`/store/orders/${orderNumber}/`).then((res) => {
      setOrder(res.data);
    });
  }, [orderNumber]);

  if (!order) {
    return <p>載入中...</p>;
  }

  return (
    <div>
      <h2>訂單詳情</h2>

      <p>訂單編號：{order.order_number}</p>
      <p>狀態：{order.status}</p>
      <p>收件人：{order.receiver_name}</p>
      <p>地址：{order.address}</p>

      <h3>商品明細</h3>
      <ul>
        {order.items.map((item, idx) => (
          <li key={idx}>
            {item.product_name} × {item.quantity}  
            （小計：{item.item_subtotal}）
          </li>
        ))}
      </ul>

      <p>總金額：{order.total_amount}</p>

      <button onClick={onBack}>返回列表</button>
    </div>
  );
}
