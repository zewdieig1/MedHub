// src/App.js

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import HomePage from "./pages/HomePage"; // You must create this file

function App() {
  return (
    <Router>
      <Routes>
        {/* Login / Signup page */}
        <Route path="/" element={<LoginPage />} />

        {/* Home page after login */}
        <Route path="/home" element={<HomePage />} />
      </Routes>
    </Router>
  );
}

export default App;
