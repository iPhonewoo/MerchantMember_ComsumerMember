import { useState } from "react";
import client from "../api/client";
import { useCart } from "../context/CartContext";

const CheckoutPage = () => {
  const { cart, clearCart } = useCart();

  const [receiverName, setReceiverName] = useState("");
  const [receiverPhone, setReceiverPhone] = useState("");
  const [address, setAddress] = useState("");
  const [note, setNote] = useState("");

  const submitOrder = async () => {
    if (cart.length === 0) {
      alert("購物車是空的");
      return;
    }

    const payload = {
      receiver_name: receiverName,
      receiver_phone: receiverPhone,
      address,
      note,
      items: cart.map(item => ({
        product: item.productId,
        quantity: item.quantity,
      })),
    };

    console.log("CART RAW =", cart);

    cart.forEach((item, idx) => {
      console.log(`ITEM ${idx}`, item);
      console.log(`ITEM ${idx} productId =`, item.productId);
    });


    try {
      await client.post("/store/orders/", payload);
      alert("下單成功！");
      clearCart();
    } catch (err) {
      alert("下單失敗");
      console.error(err.response?.data);
    }
  };

  return (
    <div>
      <h1>結帳</h1>

      <input
        placeholder="收件人姓名"
        value={receiverName}
        onChange={e => setReceiverName(e.target.value)}
      />

      <input
        placeholder="收件人電話"
        value={receiverPhone}
        onChange={e => setReceiverPhone(e.target.value)}
      />

      <input
        placeholder="地址"
        value={address}
        onChange={e => setAddress(e.target.value)}
      />

      <textarea
        placeholder="備註"
        value={note}
        onChange={e => setNote(e.target.value)}
      />

      <button onClick={submitOrder}>
        送出訂單
      </button>
    </div>
  );
};

export default CheckoutPage;
