// axios + baseURL + token
// src/api/client.js
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const client = axios.create({
  baseURL: API_BASE_URL,
});

client.interceptors.request.use(config => {
  const token = localStorage.getItem("access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error)
);

/* =========================
   Response interceptor
   access 過期時自動 refresh
========================= */
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 如果是 401，且尚未嘗試 refresh
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      try {
        const refresh = localStorage.getItem("refresh");

        const res = await axios.post(
          "/member/token/refresh/",
          { refresh }
        );

        // 存新的 access token
        localStorage.setItem("access", res.data.access);

        // 更新 header，重送原請求
        originalRequest.headers.Authorization =
          `Bearer ${res.data.access}`;

        return client(originalRequest);
      } catch (refreshError) {
        // refresh 也失敗 → 強制登出
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default client;