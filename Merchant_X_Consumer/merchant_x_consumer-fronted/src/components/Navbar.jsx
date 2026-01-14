import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login", { replace: true });
  };

  return (
    <div style={{ display: "flex", gap: 8, padding: 12 }}>
      <Link to="/">商品</Link>
      <Link to="/cart">購物車</Link>
      <Link to="/checkout">結帳</Link>
      <Link to="/create-product">上架商品</Link>
      <Link to="/orders">我的訂單</Link>
      <button onClick={handleLogout}>登出</button>
    </div>
  );
}
