// create / list orders
// src/api/order.js
import client from "./client";

export const createOrder = (data) =>
  client.post("/store/orders/", data);

export const getMyOrders = () =>
  client.get("/store/orders/");
