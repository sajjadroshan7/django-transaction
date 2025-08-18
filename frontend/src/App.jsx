import react from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import Register from "./pages/Register"
import Home from "./pages/Home"
import NotFound from "./pages/NotFound"
import UserProfile from "./pages/UserProfile"
import TransactionPage from "./pages/TransactionPage"
import ProtectedRoute from "./components/ProtectedRoute"
import Navbar from "./components/Navbar";

function Logout() {
  localStorage.clear()
  return <Navigate to="/login" />
}

function RegisterAndLogout() {
  localStorage.clear()
  return <Register />
}

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/register" element={<RegisterAndLogout />} />
        <Route path="/profile" element={<UserProfile />} />
        <Route path="*" element={<NotFound />}></Route>
        <Route path="/transaction" element = {<TransactionPage/>}></Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
