import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("member");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await client.post("/member/register/", {
        username,
        password,
        email,
        role,
      });

      // ✅ 註冊成功 → 回登入頁
      navigate("/login", { replace: true });
    } catch (err) {
      // 可依後端回傳細分
      setError("註冊失敗，帳號可能已存在");
    }
  };

  return (
    <div>
      <h2>註冊</h2>

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

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <br />

        <div>
          <label>
            <input
              type="radio"
              name="role"
              value="member"
              checked={role === "member"}
              onChange={(e) => setRole(e.target.value)}
            />
            會員
          </label>

          <label style={{ marginLeft: "12px" }}>
            <input
              type="radio"
              name="role"
              value="merchant"
              checked={role === "merchant"}
              onChange={(e) => setRole(e.target.value)}
            />
            商家
          </label>
        </div>
        <br />

        <button type="submit">註冊</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* 回登入 */}
      <p>
        已經有帳號？
        <button
          type="button"
          onClick={() => navigate("/login")}
          style={{ marginLeft: "8px" }}
        >
          回登入
        </button>
      </p>
    </div>
  );
}
