// login API
// src/api/auth.js
import client from "./client";

export const login = (data) =>
  client.post("/member/login/", data);
