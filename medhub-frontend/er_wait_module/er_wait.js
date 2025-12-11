// Cesar Alvarez and Rosario Escalara 
// ER Wait Times Module (HTML + JS)
/* This file loads ER wait data and displays it on MedHub */

// ====== 1. CONFIG ======
const API_KEY = "CL1sgU86gTv/4PaSZtvQ0g==RmXSItOx7TBnI8zr";  

const BELOIT_URL =
  "https://api.api-ninjas.com/v1/hospitals?name=beloit";
const CHICAGO_URL =
  "https://api.api-ninjas.com/v1/hospitals?city=Chicago&state=IL";

// ===== 2. DOM ELEMENTS =====
const statusDiv = document.getElementById("er-status");
const listDiv = document.getElementById("er-list");

// ===== 3. SAMPLE HOSPITAL (JANESVILLE) =====
// (Beloit and Chicago will now come from the real API)
const localHospitals = [
  {
    hospitalName: "SSM Health St. Mary's Hospital ER",
    city: "Janesville, WI",
    currentWaitMinutes: 20, // sample value
  },
];

// ===== 4. HELPERS =====
function getTrendText(minutes) {
  if (minutes >= 40) return "▲ high";
  if (minutes >= 30) return "▲ slightly up";
  if (minutes >= 20) return "— steady";
  if (minutes >= 10) return "▼ easing";
  return "▼ improving";
}

function renderHospitals(hospitals) {
  listDiv.innerHTML = "";

  hospitals.forEach((h) => {
    const card = document.createElement("div");
    card.className = "er-card";

    const trend = getTrendText(h.currentWaitMinutes);

    card.innerHTML = `
      <h3>${h.hospitalName}</h3>
      <p>${h.city}</p>
      <p><strong>${h.currentWaitMinutes} min</strong> wait · ${trend}</p>
    `;

    listDiv.appendChild(card);
  });
}

// Helper to call API Ninjas and map results into our shape
async function fetchHospitals(url) {
  const response = await fetch(url, {
    headers: {
      "X-Api-Key": API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error("API error: " + response.status);
  }

  const data = await response.json();

  return data.map((item) => {
    // Simulated wait time, since API doesn’t give real waits
    const fakeWait = Math.floor(Math.random() * 50) + 10; // 10–59 minutes

    return {
      hospitalName: item.name || item.hospital_name || "Hospital",
      city: `${item.city}, ${item.state}`,
      currentWaitMinutes: fakeWait,
    };
  });
}

// ===== 5. LOAD DATA (JANESVILLE + BELOIT + CHICAGO) =====
async function loadERData() {
  let allHospitals = [...localHospitals];

  statusDiv.textContent =
    "Loading real hospital data for Beloit and Chicago from API Ninjas (wait times simulated)...";

  try {
    // Run Beloit + Chicago requests in parallel
    const [beloitHospitals, chicagoHospitals] = await Promise.all([
      fetchHospitals(BELOIT_URL),
      fetchHospitals(CHICAGO_URL),
    ]);

    // Only keep the first Beloit result to avoid duplicates
    const beloits = beloitHospitals.slice(0, 1);
    const chicagos = chicagoHospitals.slice(0, 5);

    allHospitals = [...localHospitals, ...beloits, ...chicagos];
    statusDiv.textContent = "";
  } catch (err) {
    console.error("Error loading API data:", err);
    statusDiv.textContent =
      "Could not load API Ninjas data. Showing only Janesville sample hospital.";
  }

  renderHospitals(allHospitals);
}

// ===== 6. RUN ON PAGE LOAD =====
window.addEventListener("DOMContentLoaded", loadERData);
