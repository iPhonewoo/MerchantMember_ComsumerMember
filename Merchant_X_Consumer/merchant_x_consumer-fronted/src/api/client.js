// axios + baseURL + token
// src/api/client.js
import axios from "axios";

const client = axios.create({
  baseURL: "https://merchant-x-consumer-api.onrender.com",
});

client.interceptors.request.use(config => {
  const token = localStorage.getItem("access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default client;