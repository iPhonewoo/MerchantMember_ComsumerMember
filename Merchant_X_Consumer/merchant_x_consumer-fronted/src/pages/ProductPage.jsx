import { useEffect, useState } from "react";
import client from "../api/client";
import { useCart } from "../context/CartContext";


export default function ProductPage({ onOrder }) {
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const [next, setNext] = useState(null);
  const [previous, setPrevious] = useState(null);
  const [loading, setLoading] = useState(false);

  const { addToCart } = useCart();

  useEffect(() => {
    fetchProducts(page);
  }, [page]);

  const fetchProducts = async (page) => {
    setLoading(true);
    try {
      const res = await client.get(
        `/store/products/?page=${page}`
      );
      setProducts(res.data.results);
      setCount(res.data.count);
      setNext(res.data.next);
      setPrevious(res.data.previous);
    } catch (err) {
      console.error("取得商品失敗", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>商品列表</h2>

      {loading && <p>載入中...</p>}

      {products.map((p) => (
        <div key={p.id} style={{ border: "1px solid #ccc", margin: 10 }}>
          <p>{p.name}</p>
          <p>價格：{p.price}</p>
          <p>庫存：{p.stock}</p>

          <button onClick={() => addToCart(p)}>
            加入購物車
          </button>
        </div>
      ))}
      <div style={{ marginTop: "20px" }}>
        <button
          onClick={() => setPage(page - 1)}
          disabled={!previous}
        >
          上一頁
        </button>

        <span style={{ margin: "0 10px" }}>
          第 {page} 頁
        </span>

        <button
          onClick={() => setPage(page + 1)}
          disabled={!next}
        >
          下一頁
        </button>
      </div>
    </div>
  );
}