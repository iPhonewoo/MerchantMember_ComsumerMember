import { useEffect, useState } from "react";
import client from "../api/client";

export default function ProductPage({ onOrder }) {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    client.get("/store/products/").then((res) => {
      setProducts(res.data.results);
    });
  }, []);

  return (
    <div>
      <h2>商品列表</h2>

      {products.map((p) => (
        <div key={p.id} style={{ border: "1px solid #ccc", margin: 10 }}>
          <p>{p.name}</p>
          <p>價格：{p.price}</p>
          <p>庫存：{p.stock}</p>

          <button onClick={() => onOrder(p.id)}>下單</button>
        </div>
      ))}
    </div>
  );
}
