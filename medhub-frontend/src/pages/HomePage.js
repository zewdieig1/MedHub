// src/pages/HomePage.js

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

function HomePage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");

  // Read cookie to show who is logged in
  useEffect(() => {
    const userCookie = document.cookie
      .split("; ")
      .find((row) => row.startsWith("demo_user="));

    if (!userCookie) {
      navigate("/"); // not logged in
      return;
    }

    const userEmail = userCookie.split("=")[1];
    setEmail(userEmail);
  }, [navigate]);

  // Logout: delete cookie + go to login page
  const handleLogout = () => {
    document.cookie =
      "demo_user=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

    navigate("/");
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Welcome to MedHub</h1>

      <p style={styles.text}>Logged in as: <strong>{email}</strong></p>

      <button style={styles.logoutButton} onClick={handleLogout}>
        Logout
      </button>
    </div>
  );
}

export default HomePage;

// ----------------------------------------
// Inline Styles (simple, clean)
// ----------------------------------------
const styles = {
  container: {
    backgroundColor: "#000",
    color: "white",
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    fontFamily: "Arial, sans-serif",
  },
  title: {
    fontSize: "32px",
    marginBottom: "20px",
  },
  text: {
    fontSize: "18px",
    marginBottom: "30px",
  },
  logoutButton: {
    padding: "12px 25px",
    backgroundColor: "white",
    color: "black",
    border: "none",
    borderRadius: "10px",
    cursor: "pointer",
    fontSize: "16px",
    transition: "0.3s",
  },
};


