import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./LoginPage.css";

const API_BASE = "http://127.0.0.1:8000";

function LoginPage() {
  const navigate = useNavigate();
  const [isSignup, setIsSignup] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });
  const [message, setMessage] = useState("");

  const toggleForm = () => {
    setIsSignup(!isSignup);
    setMessage("");
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const url = isSignup
        ? `${API_BASE}/api/auth/signup`
        : `${API_BASE}/api/auth/login`;

      const payload = isSignup
        ? formData
        : { email: formData.email, password: formData.password };

      const res = await axios.post(url, payload, { withCredentials: true });

      setMessage(res.data.message);

      if (!isSignup) {
        setTimeout(() => navigate("/home"), 500);
      }

    } catch (err) {
      const detail =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Something went wrong";
      setMessage(detail);
    }
  };

  return (
    <div className="auth-fade-container">
      <div className="form-box">
        <h1>{isSignup ? "Create Account" : "MedHub Login"}</h1>

        <form onSubmit={handleSubmit}>

          {isSignup && (
            <input
              type="text"
              name="name"
              placeholder="Full Name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          )}

          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />

          <button type="submit">
            {isSignup ? "Sign Up" : "Login"}
          </button>
        </form>

        <p>
          {isSignup ? "Already have an account?" : "Don’t have an account?"}{" "}
          <button onClick={toggleForm}>
            {isSignup ? "Log In" : "Sign Up"}
          </button>
        </p>

        {message && <p>{message}</p>}
      </div>
    </div>
  );
}

export default LoginPage;
