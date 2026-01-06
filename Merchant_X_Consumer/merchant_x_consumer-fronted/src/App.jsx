// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <div>
//         <a href="https://vite.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.jsx</code> and save to test HMR
//         </p>
//       </div>
//       <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p>
//     </>
//   )
// }

// export default App

import { useState } from "react";
import LoginPage from "./pages/LoginPage";
import ProductPage from "./pages/ProductPage";
import OrderPage from "./pages/OrderPage";
import OrderListPage from "./pages/OrderListPage";
import OrderDetailPage from "./pages/OrderDetailPage";

function App() {
  const [loggedIn, setLoggedIn] = useState(
    !!localStorage.getItem("access")
  );
  const [productId, setProductId] = useState(null);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [page, setPage] = useState("products");

  if (!loggedIn) {
    return <LoginPage onLogin={() => setLoggedIn(true)} />;
  }

  if (selectedOrder) {
    return (
      <OrderDetailPage
        orderNumber={selectedOrder}
        onBack={() => setSelectedOrder(null)}
      />
    );
  }

  if (productId) {
    return (
      <OrderPage
        productId={productId}
        onDone={() => {
          setProductId(null);
          setPage("orders");
        }}
      />
    );
  }

  if (page === "orders") {
    return (
      <OrderListPage
        onSelect={(orderNumber) => setSelectedOrder(orderNumber)}
      />
    );
  }

  return (
    <div>
      <button onClick={() => setPage("products")}>商品</button>
      <button onClick={() => setPage("orders")}>我的訂單</button>

      <ProductPage onOrder={(id) => setProductId(id)} />
    </div>
  );
}

export default App;
