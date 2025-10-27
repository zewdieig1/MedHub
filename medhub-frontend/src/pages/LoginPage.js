import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./LoginPage.css";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 2500); // 2.5 s splash
    return () => clearTimeout(timer);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://127.0.0.1:8000/login", {
        email,
        password,
      });
      setMessage(res.data.message);
      navigate("/home");
    } catch (err) {
      setMessage(err.response?.data?.detail || "Login failed");
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <svg
          className="medhub-logo"
          viewBox="0 0 100 100"
          xmlns="http://www.w3.org/2000/svg"
        >
          <rect
            x="25"
            y="25"
            width="50"
            height="50"
            rx="10"
            ry="10"
            fill="none"
            stroke="white"
            strokeWidth="4"
          />
          <path
            d="M50 32 L50 68 M35 50 L65 50"
            stroke="white"
            strokeWidth="4"
            strokeLinecap="round"
          />
        </svg>
        <h1 className="loading-text">MedHub</h1>
      </div>
    );
  }

  return (
    <div className="login-container">
      <h1 className="login-title">🏥 MedHub Login</h1>
      <form onSubmit={handleSubmit} className="login-form">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="login-input"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="login-input"
        />
        <button type="submit" className="login-button">
          Login
        </button>
      </form>
      <p className="login-message">{message}</p>
    </div>
  );
}

export default LoginPage;

