import { useCart } from "../context/CartContext";
import { Link } from "react-router-dom";

const CartPage = () => {
  const { cart } = useCart();

  if (cart.length === 0) return <p>購物車是空的</p>;

  return (
    <div>
      <h1>購物車</h1>
      {cart.map(item => (
        <div key={item.productId}>
          {item.name} x {item.quantity}
        </div>
      ))}
      <Link to="/checkout">前往結帳</Link>
    </div>
  );
};

export default CartPage;
