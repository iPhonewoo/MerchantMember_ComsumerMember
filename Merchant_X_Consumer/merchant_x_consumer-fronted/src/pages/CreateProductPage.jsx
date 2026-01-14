import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function CreateProductPage() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [stock, setStock] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    try {
      await client.post("/store/products/", {
        name,
        price,
        description,
        stock,
      });
    } catch (err) {
      if (!err.response) {
        setError("無法連線到伺服器");
      } else if (err.response.status === 401) {
        setError("尚未登入");
      } else if (err.response.status === 403) {
        setError("你沒有上架商品的權限");
      } else if (err.response.status === 400) {
        setError("資料格式錯誤");
      } else {
        setError("上架失敗");
      }
      return; // ❗ 失敗就停在這
    }

    // ✅ 只有成功才會走到這裡
    setSuccess(true);

    // 給使用者一點回饋，再導頁（UX 很重要）
    setTimeout(() => {
      navigate("/merchant/products");
    }, 1000);
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

      {success && <p style={{ color: "green" }}>🎉 上架成功！</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
