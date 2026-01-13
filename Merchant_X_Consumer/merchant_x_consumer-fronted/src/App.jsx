import { Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import ProductPage from "./pages/ProductPage";
import CartPage from "./pages/CartPage";
import CheckoutPage from "./pages/CheckoutPage";
import CreateProductPage from "./pages/CreateProductPage";
import Navbar from "./components/Navbar";

function ProtectedRoute({ children }) {
  const loggedIn = !!localStorage.getItem("access");
  if (!loggedIn) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AuthLayout({ children }) {
  return (
    <>
      <Navbar />
      {children}
    </>
  );
}

function App() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login", { replace: true });
  };

  return (
      <Routes>
        {/* 登入頁 */}
        <Route path="/login" element={<LoginPage />} />

        {/* 需要登入的頁面 */}
        <Route path="/" element={
                        <AuthLayout>
                          <ProtectedRoute>
                            <ProductPage />
                          </ProtectedRoute>
                        </AuthLayout>
                        } 
                        />
        <Route path="/cart" element={
                         <AuthLayout>
                          <ProtectedRoute>
                            <CartPage />
                          </ProtectedRoute>
                        </AuthLayout>
                        } 
                        />
        <Route path="/checkout" element={
                        <AuthLayout>  
                          <ProtectedRoute>
                            <CheckoutPage />
                          </ProtectedRoute>
                        </AuthLayout>
                        } 
                        />
        <Route path="/create-product" element={
                        <AuthLayout>  
                          <ProtectedRoute>
                            <CreateProductPage />
                          </ProtectedRoute>
                        </AuthLayout>
                        } 
                        />
        
        {/* 其他路徑一律導回首頁 */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
  );
}

export default App;
