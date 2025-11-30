from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import re
import math

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
    customer_service_local: Optional[str]
    customer_service_toll_free: Optional[str]
    customer_service_tty: Optional[str]

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

def safe_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    s = str(val)
    if s.strip() == "":
        return None
    return s

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
      color: #e5e7eb;
    }}
    .tab.active {{
      border-bottom-color: #22c55e;
      color: #e5e7eb;
      background: linear-gradient(90deg, #0f172a 0%, #0f766e 50%, #22c55e 100%);
      font-weight: 700;
    }}
    .tab:hover {{
      background: linear-gradient(90deg, #0f172a 0%, #0f766e 60%, #22c55e 100%);
    }}
    .bookmark-badge {{
      position: absolute;
      top: 0.6rem;
      right: 0.6rem;
      font-size: 2rem;
      cursor: pointer;
      z-index: 10;
      transition: transform 0.2s;
      color: #22c55e;
    }}
    .bookmark-badge:hover {{
      transform: scale(1.2) rotate(-8deg);
      filter: drop-shadow(0 0 10px #22c55e);
    }}
    .plan-card {{
      background: linear-gradient(135deg, #020617 0%, #0f172a 60%, #0f766e 100%);
      border-radius: 18px;
      box-shadow: 0 4px 24px rgba(15,23,42,0.8);
      transition: box-shadow 0.3s, transform 0.3s;
      color: #e5e7eb;
    }}
    .plan-card:hover, .plan-card:focus {{
      box-shadow: 0 6px 32px rgba(34,197,94,0.4);
      transform: translateY(-3px) scale(1.01);
      outline: none;
    }}
    .filter-box {{
      background: linear-gradient(120deg, #020617 0%, #0f172a 60%, #0f766e 100%);
      border-radius: 14px;
      box-shadow: 0 6px 24px rgba(15,23,42,0.9);
      color: #e5e7eb;
    }}
    .modal-content {{
      background: linear-gradient(135deg, #020617 0%, #0f172a 60%, #0f766e 100%);
      border-radius: 16px;
      max-height: 80vh;
      overflow-y: auto;
      color: #e5e7eb;
    }}
    body {{
      background: radial-gradient(circle at top, #020617 0%, #020617 45%, #020617 100%);
      color: #e5e7eb;
    }}
    .external-link {{
      display: inline-block;
      padding: 0.5rem 1rem;
      background: linear-gradient(90deg, #22c55e 0%, #14b8a6 100%);
      color: #0f172a;
      border-radius: 0.5rem;
      text-decoration: none;
      margin: 0.5rem 0;
      transition: transform 0.2s, box-shadow 0.2s;
      font-weight: 600;
    }}
    .external-link:hover {{
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(34,197,94,0.5);
    }}
    .modal-section {{
      margin: 1rem 0;
      padding: 1rem;
      background: rgba(15, 23, 42, 0.8);
      border-radius: 0.5rem;
    }}
  </style>
</head>
<body class="min-h-screen">
  <header class="bg-slate-950 shadow-lg py-7 px-6 rounded-b-3xl mb-1 flex flex-col sm:flex-row items-center justify-between">
    <div>
      <h1 class="text-3xl sm:text-4xl font-extrabold text-gray-100 tracking-tight mb-1">
        <span class="text-white" id="state-title-span">
          {"Wisconsin" if state=="WI" else "Illinois"} Dental Plans
        </span>
      </h1>
      <p class="text-lg text-gray-300 font-medium">Compare and filter 2025 individual dental coverage</p>
      <!-- STATE TOGGLE BUTTONS -->
      <div class="mt-3 flex gap-3 items-center">
        <button
          type="button"
          onclick="changeState('WI')"
          class="px-3 py-1 rounded-full text-xs font-semibold border
                 border-teal-400 text-teal-200 bg-slate-900/70 hover:bg-teal-500 hover:text-slate-950"
        >
          Wisconsin
        </button>
        <button
          type="button"
          onclick="changeState('IL')"
          class="px-3 py-1 rounded-full text-xs font-semibold border
                 border-teal-400 text-teal-200 bg-slate-900/70 hover:bg-teal-500 hover:text-slate-950"
        >
          Illinois
        </button>
      </div>
    </div>
    <img src="https://cdn.jsdelivr.net/gh/hfg-gmuend/openmoji@latest/color/svg/1F9B7.svg" alt="Tooth Icon" class="w-16 h-16 hidden sm:block ml-4" style="filter: drop-shadow(0 2px 8px rgba(34,197,94,0.6));" />
  </header>
  <main class="max-w-7xl mx-auto px-4 py-7">
    <div class="bg-slate-900/60 rounded-t-2xl shadow mb-0 border border-slate-800">
      <div class="flex border-b border-slate-700">
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
      <div class="grid md:grid-cols-3 gap-6 items-start">
        <div class="md:col-span-2">
          <div class="grid md:grid-cols-4 gap-5">
            <input id="search" placeholder="Search plans..." class="border border-slate-600 bg-slate-900 text-gray-700 px-3 py-2 rounded-lg w-full focus:ring focus:ring-teal-500/40 transition" />
            <select id="countyFilter"class="border border-slate-600 px-3 py-2 rounded-lg w-full bg-slate-900 text-gray-700 focus:ring focus:ring-teal-500/40">
              <option value="" class="text-gray-800">All Counties</option>
            </select>
            <select id="issuerFilter" class="border border-slate-600 px-3 py-2 rounded-lg w-full bg-slate-900 text-gray-700 focus:ring focus:ring-teal-500/40">
              <option value="" class="text-gray-800">All Counties</option>
            </select>
            <select id="typeFilter" class="border border-teal-500 px-3 py-2 rounded-lg w-full bg-slate-900 text-gray-700 focus:ring focus:ring-teal-500/40">
              <option value="" class="text-gray-800">All Counties</option>
            </select>
          </div>
        </div>

        <div id="your-plan-panel" class="mt-5 md:mt-0 bg-slate-900/80 rounded-xl shadow-md p-4 border border-slate-700">
          <h3 class="text-lg font-semibold text-gray-100 mb-2">Your Plan</h3>
          <p id="your-plan-empty" class="text-sm text-gray-400">
            You have not selected a plan yet.
          </p>
          <div id="your-plan-content" class="hidden text-sm text-gray-200 space-y-1">
            <p><span class="font-semibold text-teal-300">Name:</span> <span id="your-plan-name"></span></p>
            <p><span class="font-semibold text-teal-300">Plan ID:</span> <span id="your-plan-id"></span></p>
            <p><span class="font-semibold text-teal-300">County:</span> <span id="your-plan-county"></span></p>
            <p><span class="font-semibold text-teal-300">Type:</span> <span id="your-plan-type"></span></p>
            <button onclick="clearYourPlan()" class="mt-2 px-3 py-1 rounded-full bg-red-500 text-white text-xs font-semibold hover:bg-red-600">
              Clear selection
            </button>
          </div>
        </div>
      </div>
    </div>

    <div id="plans" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"></div>
    <div id="bookmarked-plans" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 hidden"></div>
    <div id="empty-bookmarks" class="hidden bg-slate-900/80 p-14 rounded-2xl shadow text-center flex flex-col items-center justify-center border border-slate-700">
      <img src="https://cdn.jsdelivr.net/gh/hfg-gmuend/openmoji@latest/color/svg/1F516.svg" alt="Bookmark Icon" class="w-20 h-20 mt-2 mb-6"/>
      <h3 class="text-2xl font-bold text-gray-100 mb-2">No Bookmarked Plans</h3>
      <p class="text-gray-400 mb-3">Click the bookmark icon ⭐ on any plan to save it here for quick access.</p>
      <button onclick="switchTab('all')" class="mt-4 px-8 py-2 rounded-full bg-gradient-to-r from-green-500 via-teal-500 to-green-400 text-slate-950 text-lg font-bold shadow transition hover:scale-105">
        Browse All Plans
      </button>
    </div>
    <div id="history-section" class="hidden bg-slate-900/80 p-7 rounded-2xl shadow-lg mt-7 border border-slate-700">
      <h2 class="text-xl font-bold text-gray-100 mb-3">Viewer History</h2>
      <ul id="history-list" class="text-base text-gray-300 space-y-3"></ul>
    </div>
    <div id="modal" class="fixed inset-0 bg-black bg-opacity-70 hidden items-center justify-center z-50 transition">
      <div class="modal-content max-w-2xl w-full rounded-xl shadow-2xl p-8 relative flex flex-col border border-teal-600/60">
        <button onclick="closeModal()" class="absolute top-3 right-3 text-teal-300 hover:text-green-400 text-3xl focus:outline-none bg-slate-900/80 px-2 py-1 rounded-full border border-slate-700">
          &times;
        </button>
        <h2 id="modalTitle" class="text-2xl font-bold mb-2 text-gray-100"></h2>
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

  // Update header title on initial load to match state from URL/localStorage
  window.addEventListener('DOMContentLoaded', () => {{
    const titleSpan = document.getElementById('state-title-span');
    if (titleSpan) {{
      titleSpan.textContent = (state === 'WI' ? 'Wisconsin' : 'Illinois') + ' Dental Plans';
    }}
  }});

  function changeState(newState) {{
    state = newState;
    localStorage.setItem('selectedState', newState);
    const titleSpan = document.getElementById('state-title-span');
    if (titleSpan) {{
      titleSpan.textContent = (newState === 'WI' ? 'Wisconsin' : 'Illinois') + ' Dental Plans';
    }}
    fetchFilters();
    fetchPlans();
  }}

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
      <h2 class="text-xl font-semibold text-gray-100 pr-10">${{plan.plan_name}}</h2>
      <p class="text-gray-300 text-base">${{plan.plan_id}} <span class="mx-2 text-gray-500">|</span> ${{plan.issuer_name}}</p>
      <p class="text-base text-gray-300 mt-1">
        <span class="font-medium text-teal-300">County:</span> ${{plan.county}}
        <span class="mx-2 text-gray-500">|</span>
        <span class="font-medium text-teal-300">Type:</span> ${{plan.plan_type}}
      </p>
      <div class="mt-3 text-sm space-y-1 text-gray-200">
        <p><span class="font-semibold text-teal-300">Customer Service Local:</span> ${{plan.customer_service_local || 'Not listed'}}</p>
        <p><span class="font-semibold text-teal-300">Customer Service Toll Free:</span> ${{plan.customer_service_toll_free || 'Not listed'}}</p>
        <p><span class="font-semibold text-teal-300">Customer Service TTY:</span> ${{plan.customer_service_tty || 'Not listed'}}</p>
      </div>
      <button 
        type="button"
        onclick="setYourPlan(
          '${{plan.plan_id}}', 
          '${{String(plan.plan_name).replace(/'/g, "\\'")}}', 
          '${{String(plan.county).replace(/'/g, "\\'")}}', 
          '${{String(plan.plan_type).replace(/'/g, "\\'")}}', 
          event
        )"
        class="mt-3 inline-flex items-center px-3 py-1 rounded-full bg-gradient-to-r from-green-500 to-teal-500 text-slate-950 text-xs font-semibold shadow hover:shadow-lg">
        ✅ Set as Your Plan
      </button>
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
      extraDataHtml = '<div class="modal-section"><h3 class="font-semibold text-teal-300 mb-2">Additional Information</h3>';
      for (const [key, value] of Object.entries(details.extra_data)) {{
        if (value !== null && value !== '') {{
          extraDataHtml += `<p class="text-sm text-gray-200"><strong>${{key}}:</strong> ${{value}}</p>`;
        }}
      }}
      extraDataHtml += '</div>';
    }}

    content.innerHTML = `
      <div class="modal-section">
        <p class="text-gray-200"><strong class="text-teal-300">Plan ID:</strong> ${{details.plan_id}}</p>
        <p class="text-gray-200"><strong class="text-teal-300">Issuer:</strong> ${{details.issuer_name}}</p>
        <p class="text-gray-200"><strong class="text-teal-300">County:</strong> ${{details.county}}</p>
        <p class="text-gray-200"><strong class="text-teal-300">Plan Type:</strong> ${{details.plan_type}}</p>
        ${{details.rating_area ? `<p class="text-gray-200"><strong class="text-teal-300">Rating Area:</strong> ${{details.rating_area}}</p>` : ''}}
        ${{details.child_only_offering ? `<p class="text-gray-200"><strong class="text-teal-300">Child Only Offering:</strong> ${{details.child_only_offering}}</p>` : ''}}
        ${{details.metal_level ? `<p class="text-gray-200"><strong class="text-teal-300">Metal Level:</strong> ${{details.metal_level}}</p>` : ''}}
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
      list.innerHTML = '<li class="text-gray-500">No plans viewed yet.</li>';
    }} else {{
      history.slice().reverse().forEach(entry => {{
        const date = new Date(entry.timestamp);
        const formatted = date.toLocaleString();
        const li = document.createElement('li');
        li.innerHTML = `<strong class="text-gray-100">${{entry.plan_name}}</strong> <span class="text-teal-300">(${{entry.county}})</span> <span class="text-gray-400 ml-2">[${{formatted}}]</span>`;
        list.appendChild(li);
      }});
    }}
    document.getElementById('history-section').classList.remove('hidden');
  }}

  function closeModal() {{
    document.getElementById("modal").classList.add("hidden");
    document.getElementById("modal").classList.remove("flex");
  }}

  function setYourPlan(planId, planName, county, planType, event) {{
    event.stopPropagation();
    const yourPlan = {{ plan_id: planId, plan_name: planName, county: county, plan_type: planType }};
    localStorage.setItem('yourPlan', JSON.stringify(yourPlan));
    renderYourPlanPanel();
  }}

  function clearYourPlan() {{
    localStorage.removeItem('yourPlan');
    renderYourPlanPanel();
  }}

  function renderYourPlanPanel() {{
    const raw = localStorage.getItem('yourPlan');
    const emptyEl = document.getElementById('your-plan-empty');
    const contentEl = document.getElementById('your-plan-content');
    if (!emptyEl || !contentEl) return;

    if (!raw) {{
      emptyEl.classList.remove('hidden');
      contentEl.classList.add('hidden');
      return;
    }}

    const p = JSON.parse(raw);
    document.getElementById('your-plan-name').innerText = p.plan_name || '';
    document.getElementById('your-plan-id').innerText = p.plan_id || '';
    document.getElementById('your-plan-county').innerText = p.county || '';
    document.getElementById('your-plan-type').innerText = p.plan_type || '';
    emptyEl.classList.add('hidden');
    contentEl.classList.remove('hidden');
  }}

  document.getElementById("countyFilter").onchange = fetchPlans;
  document.getElementById("issuerFilter").onchange = fetchPlans;
  document.getElementById("typeFilter").onchange = fetchPlans;
  document.getElementById("search").oninput = fetchPlans;

  window.onload = () => {{
    fetchFilters();
    fetchPlans();
    renderYourPlanPanel();
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
        df = df[df["State Code"].astype(str).str.strip() == state]
    if county:
        df = df[df["County Name"].astype(str).str.strip() == county]
    if issuer:
        df = df[df["Issuer Name"].astype(str).str.strip() == issuer]
    if plan_type:
        df = df[df["Plan Type"].astype(str).str.strip() == plan_type]
    if search:
        s = str(search)
        df = df[
            df["Plan Marketing Name"].astype(str).str.contains(s, case=False, na=False) |
            df["Issuer Name"].astype(str).str.contains(s, case=False, na=False) |
            df["Plan ID (Standard Component)"].astype(str).str.contains(s, case=False, na=False)
        ]


    plans: List[Plan] = []
    for _, row in df.iterrows():
        plans.append(
            Plan(
                plan_id=str(row["Plan ID (Standard Component)"]),
                plan_name=safe_str(row.get("Plan Marketing Name")),
                issuer_name=safe_str(row.get("Issuer Name")),
                county=safe_str(row.get("County Name")),
                plan_type=safe_str(row.get("Plan Type")),
                deductible=safe_str(row.get("Deductible")),
                coinsurance=safe_str(row.get("Coinsurance")),
                annual_max=safe_str(row.get("Annual Maximum")),
                network_url=safe_str(row.get("Network URL")),
                brochure_url=safe_str(row.get("Plan Brochure URL")),
                customer_service_local=safe_str(row.get("Customer Service Phone Number Local")),
                customer_service_toll_free=safe_str(row.get("Customer Service Phone Number Toll Free")),
                customer_service_tty=safe_str(row.get("Customer Service Phone Number TTY")),
            )
        )
    return plans

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
