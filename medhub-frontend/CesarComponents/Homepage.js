// src/pages/HomePage.js
import React from "react";
import WelcomeBanner from "../components/WelcomeBanner";

function HomePage() {
  return (
    <div className="homepage">
      {/* 👇 Add your welcome message here */}
      <WelcomeBanner />

      {/* Your existing homepage content */}
      <h1>MedHub Dashboard</h1>
      <p>Explore insurance plans, ER wait times, and more.</p>
    </div>
  );
}

export default HomePage;
