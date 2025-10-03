import React from "react";
import { useNavigate } from "react-router-dom";

function HomePage() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Go back to login page
    navigate("/");
  };

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h1>🏠 Welcome to MedHub</h1>
      <p>You have successfully logged in!</p>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default HomePage;

