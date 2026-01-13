import { useState } from "react";
import client from "../api/client";

export default function CreateProductPage({ onDone }) {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [stock, setStock] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await client.post("store/products/", {
        name,
        price,
        description,
        stock,
      });

      onDone(); // 通知父層「上架完成」
    } catch (err) {
      console.log("CREATE PRODUCT ERROR:", err.response);

      if (err.response?.status === 403) {
        setError("你沒有上架商品的權限");
    } else if (err.response?.status === 400) {
        setError("資料格式錯誤");
    } else if (err.response?.status === 401) {
        setError("尚未登入");
    } else {
        setError("上架失敗");
    }
  }
  };

  return (
    <div>
      <h2>上架商品</h2>

      <form onSubmit={handleSubmit}>
        <input
          placeholder="商品名稱"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <input
          type="number"
          placeholder="價格"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
        />

        <input
          type="number"
          placeholder="數量"
          value={stock}
          onChange={(e) => setStock(e.target.value)}
        />

        <textarea
          placeholder="商品描述"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <button type="submit">上架</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
