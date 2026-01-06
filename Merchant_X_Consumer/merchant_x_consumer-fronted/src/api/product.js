// get products
// src/api/product.js
import client from "./client";

export const getProducts = () =>
  client.get("/store/products/");
