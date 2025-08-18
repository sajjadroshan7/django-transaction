// components/Navbar.jsx
import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";

const Navbar = () => {
  return (
    <nav className="navbar">
      {/* Logo */}
      <div className="navbar-logo">
        <Link to="/">MyApp</Link>
      </div>

      {/* Navigation Links */}
      <div className="navbar-links">
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/register">Siginup</Link>
        <Link to="/profile">Profile</Link>
        <Link to="/logout">Logout</Link>
        <Link to="/login">Login</Link>
        <Link to="/transaction">Transaction</Link>
      </div>

      {/* Buttons / Profile */}
      <div className="navbar-buttons">
        <button>Login</button>
      </div>
    </nav>
  );
};

export default Navbar;
