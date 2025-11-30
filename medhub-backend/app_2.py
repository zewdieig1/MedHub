from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import re

app = FastAPI(title="Wisco Dental Plans")
df_plans = None

class Plan(BaseModel):
    plan_id: str
    plan_name: str
    issuer_name: str
    county: str
    plan_type: str
    deductible: Optional[str]
    coinsurance: Optional[str]
    annual_max: Optional[str]
    network_url: Optional[str]
    brochure_url: Optional[str]

class PlanDetails(BaseModel):
    plan_id: str
    plan_name: str
    issuer_name: str
    county: str
    plan_type: str
    brochure_url: Optional[str]
    network_url: Optional[str]
    rating_area: Optional[str]
    child_only_offering: Optional[str]
    metal_level: Optional[str]
    extra_data: Dict[str, Any]

@app.on_event("startup")
def load_data():
    global df_plans
    df = pd.read_excel(
        "Individual_Market_Dental.xlsx",
        sheet_name="Individual_Market_Dental",
        header=1
    )
    df = df[df["State Code"].astype(str).str.strip().isin(["WI", "IL"])]
    df.columns = df.columns.str.strip()
    df_plans = df

@app.get("/", response_class=HTMLResponse)
async def landing():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
  <title>Select State - Dental Plans</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
  <style>
    body { 
      background: radial-gradient(circle at top, #eff6ff 0%, #dbeafe 45%, #1d4ed8 100%);
    }
    .card {
      background: #ffffff;
      border-radius: 1.5rem;
      border: 1px solid #dbeafe;
      box-shadow: 0 12px 40px rgba(15, 23, 42, 0.18);
      transition: box-shadow 0.2s, transform 0.2s;
    }
    .card:hover {
      box-shadow: 0 16px 50px rgba(37, 99, 235, 0.3);
      transform: translateY(-2px);
    }
    .state-btn {
      transition: transform 0.1s, box-shadow 0.1s;
    }
    .state-btn:hover { 
      transform: scale(1.04); 
      box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
    }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center">
  <div class="card max-w-xl w-full mx-auto p-12 text-center">
    <img src="https://cdn.jsdelivr.net/gh/hfg-gmuend/openmoji@latest/color/svg/1F9B7.svg"
        class="w-20 h-20 mx-auto mb-4" style="filter: drop-shadow(0 1px 3px rgba(37,99,235,0.3));" />
    <h1 class="text-3xl font-extrabold text-blue-900 mb-3 tracking-tight">
      Wisco Dental Plans
    </h1>
    <p class="mb-8 text-blue-700 text-lg">
      Choose your state to browse individual dental coverage options.
    </p>
    <div class="flex flex-col sm:flex-row gap-6 items-center justify-center">
      <button onclick="selectState('WI')" 
              class="state-btn w-40 py-3 rounded-xl shadow bg-gradient-to-br from-blue-700 via-blue-600 to-blue-500 text-white text-xl font-semibold">
        Wisconsin
      </button>
      <button onclick="selectState('IL')" 
              class="state-btn w-40 py-3 rounded-xl shadow bg-gradient-to-br from-blue-500 via-blue-400 to-blue-300 text-blue-950 text-xl font-semibold">
        Illinois
      </button>
    </div>
  </div>
  <script>
    function selectState(state) {
      localStorage.setItem('selectedState', state);
      window.location.href = '/plans?state=' + state;
    }
  </script>
</body>
</html>
    """)

@app.get("/plans", response_class=HTMLResponse)
async def plans_page(state: Optional[str] = "WI"):
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html>
<head>
  <title>Dental Plans</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
  <style>
    .tab {{
      cursor: pointer;
      padding: 0.8rem 2rem;
      border-bottom: 4px solid transparent;
      transition: background 0.3s, border-bottom-color 0.3s;
      font-size: 1.15rem;
    }}
    .tab.active {{
      border-bottom-color: #496ddb;
      color: #243d7c;
      background: linear-gradient(90deg, #ffffff 30%, #fef08a 50%, #a4d8fa 100%);
      font-weight: 700;
    }}
    .tab:hover {{
      background: linear-gradient(90deg, #bae6fd 60%, #fef9c3 100%);
    }}
    .bookmark-badge {{
      position: absolute;
      top: 0.6rem;
      right: 0.6rem;
      font-size: 2rem;
      cursor: pointer;
      z-index: 10;
      transition: transform 0.2s;
      color: #2563eb;
    }}
    .bookmark-badge:hover {{
      transform: scale(1.2) rotate(-8deg);
      filter: drop-shadow(0 0 10px #fbcd09);
    }}
    .plan-card {{
      background: linear-gradient(120deg, #e0e7ff 0%, #bae6fd 100%);
      border-radius: 18px;
      box-shadow: 0 4px 24px rgba(32,35,89,0.08);
      transition: box-shadow 0.3s, transform 0.3s;
    }}
    .plan-card:hover, .plan-card:focus {{
      box-shadow: 0 6px 32px rgba(73,109,219,0.18);
      transform: translateY(-3px) scale(1.01);
      outline: none;
    }}
    .filter-box {{
      background: linear-gradient(90deg, #2563eb 20%, #bae6fd 70%, #fef08a 100%);
      border-radius: 14px;
      box-shadow: 0 6px 24px #cffafe44;
    }}
    .modal-content {{
      background: linear-gradient(102deg, #e0e7ff 70%, #fef9c3 100%);
      border-radius: 16px;
      max-height: 80vh;
      overflow-y: auto;
    }}
    body {{
      background: linear-gradient(to top right,#2563eb 0%, #a4d8fa 80%, #fef08a 100%);
    }}
    .external-link {{
      display: inline-block;
      padding: 0.5rem 1rem;
      background: #2563eb;
      color: white;
      border-radius: 0.5rem;
      text-decoration: none;
      margin: 0.5rem 0;
      transition: background 0.2s;
    }}
    .external-link:hover {{
      background: #1d4ed8;
    }}
    .modal-section {{
      margin: 1rem 0;
      padding: 1rem;
      background: rgba(255, 255, 255, 0.5);
      border-radius: 0.5rem;
    }}
  </style>
</head>
<body class="min-h-screen">
  <header class="bg-white shadow-lg py-7 px-6 rounded-b-3xl mb-1 flex flex-col sm:flex-row items-center justify-between">
    <div>
      <h1 class="text-3xl sm:text-4xl font-extrabold text-blue-900 tracking-tight mb-1">
        <span class="bg-gradient-to-r from-blue-700 via-blue-400 to-yellow-400 bg-clip-text text-transparent">
          {"Wisconsin" if state=="WI" else "Illinois"} Dental Plans
        </span>
      </h1>
      <p class="text-lg text-blue-700 font-medium">Compare and filter 2025 individual dental coverage</p>
    </div>
    <img src="https://cdn.jsdelivr.net/gh/hfg-gmuend/openmoji@latest/color/svg/1F9B7.svg" alt="Tooth Icon" class="w-16 h-16 hidden sm:block ml-4" style="filter: drop-shadow(0 2px 8px #60a5fa;" />
  </header>
  <main class="max-w-7xl mx-auto px-4 py-7">
    <div class="bg-gradient-to-r from-white via-blue-50 to-yellow-50 rounded-t-2xl shadow mb-0">
      <div class="flex border-b border-blue-200">
        <div class="tab active" onclick="switchTab('all')" id="tab-all">
          <span class="mr-2">🗂️</span>All Plans
        </div>
        <div class="tab" onclick="switchTab('bookmarked')" id="tab-bookmarked">
          <span class="mr-2">🔖</span>Bookmarked
        </div>
        <div class="tab" onclick="switchTab('history')" id="tab-history">
          <span class="mr-2">📜</span>History
        </div>
      </div>
    </div>
    <div class="filter-box p-5 mb-8" id="filters-section">
      <div class="grid md:grid-cols-4 gap-5">
        <input id="search" placeholder="Search plans..." class="border border-blue-700 bg-white px-3 py-2 rounded-lg w-full focus:ring focus:ring-blue-200 transition" />
        <select id="countyFilter" class="border border-blue-300 px-3 py-2 rounded-lg w-full bg-white focus:ring focus:ring-blue-200">
          <option value="">All Counties</option>
        </select>
        <select id="issuerFilter" class="border border-blue-200 px-3 py-2 rounded-lg w-full bg-white focus:ring focus:ring-blue-100">
          <option value="">All Issuers</option>
        </select>
        <select id="typeFilter" class="border border-yellow-300 px-3 py-2 rounded-lg w-full bg-white focus:ring focus:ring-yellow-100">
          <option value="">All Plan Types</option>
        </select>
      </div>
    </div>
    <div id="plans" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"></div>
    <div id="bookmarked-plans" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 hidden"></div>
    <div id="empty-bookmarks" class="hidden bg-white p-14 rounded-2xl shadow text-center flex flex-col items-center justify-center">
      <img src="https://cdn.jsdelivr.net/gh/hfg-gmuend/openmoji@latest/color/svg/1F516.svg" alt="Bookmark Icon" class="w-20 h-20 mt-2 mb-6"/>
      <h3 class="text-2xl font-bold text-blue-700 mb-2">No Bookmarked Plans</h3>
      <p class="text-blue-400 mb-3">Click the bookmark icon ⭐ on any plan to save it here for quick access.</p>
      <button onclick="switchTab('all')" class="mt-4 px-8 py-2 rounded-full bg-gradient-to-r from-blue-700 via-blue-400 to-yellow-400 text-white text-lg font-bold shadow transition hover:scale-105">Browse All Plans</button>
    </div>
    <div id="history-section" class="hidden bg-gradient-to-r from-white via-yellow-100 to-blue-50 p-7 rounded-2xl shadow-lg mt-7">
      <h2 class="text-xl font-bold text-blue-800 mb-3">Viewer History</h2>
      <ul id="history-list" class="text-base text-blue-700 space-y-3"></ul>
    </div>
    <div id="modal" class="fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50 transition">
      <div class="modal-content max-w-2xl w-full rounded-xl shadow-2xl p-8 relative flex flex-col">
        <button onclick="closeModal()" class="absolute top-3 right-3 text-blue-700 hover:text-yellow-500 text-3xl focus:outline-none bg-gradient-to-r from-blue-50 via-yellow-100 to-blue-100 px-2 py-1 rounded-full">
          &times;
        </button>
        <h2 id="modalTitle" class="text-2xl font-bold mb-2 text-blue-900"></h2>
        <div id="modalContent"></div>
      </div>
    </div>
  </main>
<script>
  function getQueryParam(param) {{
    const params = new URLSearchParams(window.location.search);
    return params.get(param);
  }}
  let state = getQueryParam('state') || localStorage.getItem('selectedState') || 'WI';
  localStorage.setItem('selectedState', state);

  let currentTab = 'all';
  let allPlansData = [];
  let bookmarkedPlanIds = new Set(JSON.parse(localStorage.getItem('bookmarkedPlans') || '[]'));

  function toggleBookmark(planId, county, event) {{
    event.stopPropagation();
    const uniqueKey = `${{planId}}__${{county}}`;
    if (bookmarkedPlanIds.has(uniqueKey)) {{
      bookmarkedPlanIds.delete(uniqueKey);
    }} else {{
      bookmarkedPlanIds.add(uniqueKey);
    }}
    localStorage.setItem('bookmarkedPlans', JSON.stringify([...bookmarkedPlanIds]));
    if (currentTab === 'bookmarked') {{
      showBookmarkedPlans();
    }} else {{
      renderPlans(allPlansData);
    }}
  }}

  function switchTab(tab) {{
    currentTab = tab;
    document.getElementById('tab-all').classList.remove('active');
    document.getElementById('tab-bookmarked').classList.remove('active');
    document.getElementById('tab-history').classList.remove('active');
    document.getElementById('tab-' + tab).classList.add('active');
    document.getElementById('filters-section').classList.add('hidden');
    document.getElementById('plans').classList.add('hidden');
    document.getElementById('bookmarked-plans').classList.add('hidden');
    document.getElementById('empty-bookmarks').classList.add('hidden');
    document.getElementById('history-section').classList.add('hidden');
    if (tab === 'all') {{
      document.getElementById('filters-section').classList.remove('hidden');
      document.getElementById('plans').classList.remove('hidden');
      fetchPlans();
    }} else if (tab === 'bookmarked') {{
      showBookmarkedPlans();
    }} else if (tab === 'history') {{
      showViewerHistory();
    }}
  }}

  async function showBookmarkedPlans() {{
    if (bookmarkedPlanIds.size === 0) {{
      document.getElementById('bookmarked-plans').classList.add('hidden');
      document.getElementById('empty-bookmarks').classList.remove('hidden');
      return;
    }}
    document.getElementById('empty-bookmarks').classList.add('hidden');
    document.getElementById('bookmarked-plans').classList.remove('hidden');
    const bookmarkedPlans = allPlansData.filter(plan => {{
      const key = `${{plan.plan_id}}__${{plan.county}}`;
      return bookmarkedPlanIds.has(key);
    }});
    const container = document.getElementById('bookmarked-plans');
    container.innerHTML = '';
    bookmarkedPlans.forEach(plan => {{
      container.appendChild(createPlanCard(plan));
    }});
  }}

  function createPlanCard(plan) {{
    const div = document.createElement('div');
    div.className = 'plan-card p-5 mb-2 cursor-pointer relative transition';
    div.tabIndex = 0;
    div.onclick = () => openModal(plan.plan_id);
    const key = `${{plan.plan_id}}__${{plan.county}}`;
    const isBookmarked = bookmarkedPlanIds.has(key);
    const bookmarkIcon = isBookmarked ? '⭐' : '☆';
    let html = `
      <div class="bookmark-badge" onclick="toggleBookmark('${{plan.plan_id}}', '${{plan.county}}', event)" title="${{isBookmarked ? 'Remove bookmark' : 'Bookmark this plan'}}">${{bookmarkIcon}}</div>
      <h2 class="text-xl font-semibold text-blue-900 pr-10">${{plan.plan_name}}</h2>
      <p class="text-blue-700 text-base">${{plan.plan_id}} <span class="mx-2">|</span> ${{plan.issuer_name}}</p>
      <p class="text-base text-blue-700 mt-1"><span class="font-medium text-blue-700">County:</span> ${{plan.county}} <span class="mx-2">|</span> <span class="font-medium text-yellow-600">Type:</span> ${{plan.plan_type}}</p>
      <div class="flex flex-wrap gap-2 mt-2 text-base">
        <span class="bg-yellow-100 px-2 py-1 rounded-md"><strong>Deductible:</strong> ${{plan.deductible || 'N/A'}}</span>
        <span class="bg-blue-100 px-2 py-1 rounded-md"><strong>Coinsurance:</strong> ${{plan.coinsurance || 'N/A'}}</span>
        <span class="bg-blue-50 px-2 py-1 rounded-md"><strong>Max:</strong> ${{plan.annual_max || 'N/A'}}</span>
      </div>
    `;
    div.innerHTML = html;
    return div;
  }}

  async function fetchFilters() {{
    const res = await fetch(`/api/filters?state=${{encodeURIComponent(state)}}`);
    const data = await res.json();
    const countySelect = document.getElementById("countyFilter");
    const issuerSelect = document.getElementById("issuerFilter");
    const typeSelect = document.getElementById("typeFilter");
    countySelect.innerHTML = '<option value="">All Counties</option>';
    data.counties.forEach(c => {{
      let o = document.createElement("option");
      o.value = c; o.text = c;
      countySelect.appendChild(o);
    }});
    issuerSelect.innerHTML = '<option value="">All Issuers</option>';
    data.issuers.forEach(i => {{
      let o = document.createElement("option");
      o.value = i; o.text = i;
      issuerSelect.appendChild(o);
    }});
    typeSelect.innerHTML = '<option value="">All Plan Types</option>';
    data.plan_types.forEach(p => {{
      let o = document.createElement("option");
      o.value = p; o.text = p;
      typeSelect.appendChild(o);
    }});
  }}

  async function fetchPlans() {{
    const county = document.getElementById("countyFilter").value;
    const issuer = document.getElementById("issuerFilter").value;
    const planType = document.getElementById("typeFilter").value;
    const search = document.getElementById("search").value;
    let url = `/api/plans?state=${{encodeURIComponent(state)}}&`;
    if (county) url += `county=${{encodeURIComponent(county)}}&`;
    if (issuer) url += `issuer=${{encodeURIComponent(issuer)}}&`;
    if (planType) url += `plan_type=${{encodeURIComponent(planType)}}&`;
    if (search) url += `search=${{encodeURIComponent(search)}}`;
    const res = await fetch(url);
    const plans = await res.json();
    allPlansData = plans;
    renderPlans(plans);
  }}

  function renderPlans(plans) {{
    const container = document.getElementById("plans");
    container.innerHTML = '';
    plans.forEach(plan => {{
      container.appendChild(createPlanCard(plan));
    }});
  }}

  async function openModal(planId) {{
    const plan = allPlansData.find(p => p.plan_id === planId);
    if (plan) {{
      const history = JSON.parse(localStorage.getItem('viewerHistory') || '[]');
      const timestamp = new Date().toISOString();
      const entry = {{
        plan_id: plan.plan_id,
        plan_name: plan.plan_name,
        county: plan.county,
        timestamp: timestamp
      }};
      if (!history.length || history[history.length - 1].plan_id !== plan.plan_id) {{
        history.push(entry);
        localStorage.setItem('viewerHistory', JSON.stringify(history));
      }}
    }}
    const res = await fetch(`/api/plans/${{planId}}/details`);
    const details = await res.json();
    document.getElementById("modalTitle").innerText = details.plan_name;
    const content = document.getElementById("modalContent");
    
    let brochureLink = '';
    if (details.brochure_url) {{
      brochureLink = `<a href="${{details.brochure_url}}" target="_blank" class="external-link">📄 View Brochure</a>`;
    }}

    let networkLink = '';
    if (details.network_url) {{
      networkLink = `<a href="${{details.network_url}}" target="_blank" class="external-link">🔗 View Network</a>`;
    }}

    let extraDataHtml = '';
    if (details.extra_data && Object.keys(details.extra_data).length > 0) {{
      extraDataHtml = '<div class="modal-section"><h3 class="font-semibold text-blue-700 mb-2">Additional Information</h3>';
      for (const [key, value] of Object.entries(details.extra_data)) {{
        if (value !== null && value !== '') {{
          extraDataHtml += `<p class="text-sm text-blue-600"><strong>${{key}}:</strong> ${{value}}</p>`;
        }}
      }}
      extraDataHtml += '</div>';
    }}

    content.innerHTML = `
      <div class="modal-section">
        <p class="text-blue-700"><strong>Plan ID:</strong> ${{details.plan_id}}</p>
        <p class="text-blue-700"><strong>Issuer:</strong> ${{details.issuer_name}}</p>
        <p class="text-blue-700"><strong>County:</strong> ${{details.county}}</p>
        <p class="text-blue-700"><strong>Plan Type:</strong> ${{details.plan_type}}</p>
        ${{details.rating_area ? `<p class="text-blue-700"><strong>Rating Area:</strong> ${{details.rating_area}}</p>` : ''}}
        ${{details.child_only_offering ? `<p class="text-blue-700"><strong>Child Only Offering:</strong> ${{details.child_only_offering}}</p>` : ''}}
        ${{details.metal_level ? `<p class="text-blue-700"><strong>Metal Level:</strong> ${{details.metal_level}}</p>` : ''}}
      </div>
      <div class="modal-section">
        ${{brochureLink}}
        ${{networkLink}}
      </div>
      ${{extraDataHtml}}
    `;
    document.getElementById("modal").classList.remove("hidden");
    document.getElementById("modal").classList.add("flex");
  }}

  function showViewerHistory() {{
    const history = JSON.parse(localStorage.getItem('viewerHistory') || '[]');
    const list = document.getElementById('history-list');
    list.innerHTML = '';
    if (history.length === 0) {{
      list.innerHTML = '<li class="text-blue-400">No plans viewed yet.</li>';
    }} else {{
      history.slice().reverse().forEach(entry => {{
        const date = new Date(entry.timestamp);
        const formatted = date.toLocaleString();
        const li = document.createElement('li');
        li.innerHTML = `<strong class="text-blue-700">${{entry.plan_name}}</strong> <span class="text-yellow-600">(${{entry.county}})</span> <span class="text-blue-400 ml-2">[${{formatted}}]</span>`;
        list.appendChild(li);
      }});
    }}
    document.getElementById('history-section').classList.remove('hidden');
  }}

  function closeModal() {{
    document.getElementById("modal").classList.add("hidden");
    document.getElementById("modal").classList.remove("flex");
  }}

  document.getElementById("countyFilter").onchange = fetchPlans;
  document.getElementById("issuerFilter").onchange = fetchPlans;
  document.getElementById("typeFilter").onchange = fetchPlans;
  document.getElementById("search").oninput = fetchPlans;

  window.onload = () => {{
    fetchFilters();
    fetchPlans();
  }};
</script>
</body>
</html>
    """)

@app.get("/api/plans", response_model=List[Plan])
async def get_plans(
    state: Optional[str] = Query("WI"),
    county: Optional[str] = Query(None),
    issuer: Optional[str] = Query(None),
    plan_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    df = df_plans.copy()
    if state:
        df = df[df["State Code"].str.strip() == state]
    if county:
        df = df[df["County Name"].str.strip() == county]
    if issuer:
        df = df[df["Issuer Name"].str.strip() == issuer]
    if plan_type:
        df = df[df["Plan Type"].str.strip() == plan_type]
    if search:
        s = search.lower()
        df = df[
            df["Plan Marketing Name"].str.lower().str.contains(s) |
            df["Issuer Name"].str.lower().str.contains(s)
        ]
    return [
        Plan(
            plan_id=row["Plan ID (Standard Component)"],
            plan_name=row["Plan Marketing Name"],
            issuer_name=row["Issuer Name"],
            county=row["County Name"],
            plan_type=row["Plan Type"],
            deductible=row.get("Deductible"),
            coinsurance=row.get("Coinsurance"),
            annual_max=row.get("Annual Maximum"),
            network_url=row.get("Network URL"),
            brochure_url=row.get("Plan Brochure URL")
        ) for _, row in df.iterrows()
    ]

@app.get("/api/filters")
async def get_filters(state: Optional[str] = Query("WI")):
    df = df_plans.copy()
    df["Plan Type"] = df["Plan Type"].astype(str).str.strip()
    if state:
        df = df[df["State Code"].astype(str).str.strip() == state]
    counties = sorted(df["County Name"].dropna().astype(str).str.strip().unique().tolist())
    issuers = sorted(df["Issuer Name"].dropna().astype(str).str.strip().unique().tolist())
    plan_types = sorted(df["Plan Type"].dropna().unique().tolist())
    return {
        "counties": counties,
        "issuers": issuers,
        "plan_types": plan_types,
    }

@app.get("/api/plans/{plan_id}/details", response_model=PlanDetails)
async def get_plan_details(plan_id: str):
    row = df_plans[df_plans["Plan ID (Standard Component)"] == plan_id].iloc[0]

    plan_name = row.get("Plan Marketing Name", "")
    issuer_name = row.get("Issuer Name", "")
    county = row.get("County Name", "")
    plan_type = row.get("Plan Type", "")
    brochure_url = row.get("Plan Brochure URL")
    network_url = row.get("Network URL")
    rating_area = row.get("Rating Area")
    child_only_offering = row.get("Child Only Offering")
    metal_level = row.get("Metal Level")

    standard_fields = {
        "Plan ID (Standard Component)", "Plan Marketing Name", "Issuer Name",
        "County Name", "Plan Type", "Plan Brochure URL", "Network URL",
        "Rating Area", "Child Only Offering", "Metal Level", "State Code",
        "Deductible", "Coinsurance", "Annual Maximum"
    }

    coverage_cols = {
        "Routine Dental Services - Adult (Coverage)",
        "Basic Dental Care - Adult (Coverage)",
        "Major Dental Care - Adult (Coverage)",
        "Orthodontia - Adult (Coverage)",
        "Dental Check-Up for Children (Coverage)",
        "Basic Dental Care - Child (Coverage)",
        "Major Dental Care - Child (Coverage)",
        "Orthodontia - Child (Coverage)",
    }

    extra_data: Dict[str, Any] = {}

    for col in df_plans.columns:
        col_lower = str(col).lower()

        if col in standard_fields:
            continue

        if "premium" in col_lower:
            continue

        if col == "Summary of Benefits URL":
            val_raw = row.get(col)
            if pd.isna(val_raw) or val_raw == "":
                continue
            extra_data[col] = str(val_raw)
            continue

        val = row.get(col)

        if pd.isna(val) or val == "":
            if col in coverage_cols:
                extra_data[col] = "Not provided"
            continue

        if col in coverage_cols:
            if str(val).strip().upper() == "X":
                extra_data[col] = "Yes"
            else:
                extra_data[col] = str(val)
        else:
            extra_data[col] = str(val)

    return PlanDetails(
        plan_id=plan_id,
        plan_name=plan_name,
        issuer_name=issuer_name,
        county=county,
        plan_type=plan_type,
        brochure_url=brochure_url,
        network_url=network_url,
        rating_area=rating_area,
        child_only_offering=child_only_offering,
        metal_level=metal_level,
        extra_data=extra_data
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
