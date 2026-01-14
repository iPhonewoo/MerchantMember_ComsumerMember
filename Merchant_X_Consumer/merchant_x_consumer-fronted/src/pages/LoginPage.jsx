import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await client.post("/member/login/", {
        username,
        password,
      });

      localStorage.setItem("access", res.data.access);
      localStorage.setItem("role", res.data.role);

      // ✅ 登入成功後，交給 Router 導頁
      navigate("/", { replace: true });
    } catch (err) {
      setError("登入失敗，帳號或密碼錯誤");
    }
  };

  return (
    <div>
      <h2>登入</h2>

      <form onSubmit={handleSubmit}>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <br />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <br />

        <button type="submit">登入</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <p>
        還沒有帳號？
        <button
          type="button"
          onClick={() => navigate("/register")}
          style={{ marginLeft: "8px" }}
        >
          註冊
        </button>
      </p>
    </div>
  );
}