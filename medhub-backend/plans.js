
function getQueryParam(param) {
  const params = new URLSearchParams(window.location.search);
  return params.get(param);
}

let state = getQueryParam('state') || localStorage.getItem('selectedState') || 'WI';
localStorage.setItem('selectedState', state);

// Update header title on initial load to match state from URL/localStorage
window.addEventListener('DOMContentLoaded', () => {
  const titleSpan = document.getElementById('state-title-span');
  if (titleSpan) {
    titleSpan.textContent = (state === 'WI' ? 'Wisconsin' : 'Illinois') + ' Dental Plans';
  }
});

function changeState(newState) {
  state = newState;
  localStorage.setItem('selectedState', newState);
  const titleSpan = document.getElementById('state-title-span');
  if (titleSpan) {
    titleSpan.textContent = (newState === 'WI' ? 'Wisconsin' : 'Illinois') + ' Dental Plans';
  }
  fetchFilters();
  fetchPlans();
}

let currentTab = 'all';
let allPlansData = [];
let bookmarkedPlanIds = new Set(JSON.parse(localStorage.getItem('bookmarkedPlans') || '[]'));

function toggleBookmark(planId, county, event) {
  event.stopPropagation();
  const uniqueKey = `${planId}__${county}`;
  if (bookmarkedPlanIds.has(uniqueKey)) {
    bookmarkedPlanIds.delete(uniqueKey);
  } else {
    bookmarkedPlanIds.add(uniqueKey);
  }
  localStorage.setItem('bookmarkedPlans', JSON.stringify([...bookmarkedPlanIds]));
  if (currentTab === 'bookmarked') {
    showBookmarkedPlans();
  } else {
    renderPlans(allPlansData);
  }
}

function switchTab(tab) {
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
  if (tab === 'all') {
    document.getElementById('filters-section').classList.remove('hidden');
    document.getElementById('plans').classList.remove('hidden');
    fetchPlans();
  } else if (tab === 'bookmarked') {
    showBookmarkedPlans();
  } else if (tab === 'history') {
    showViewerHistory();
  }
}

async function showBookmarkedPlans() {
  if (bookmarkedPlanIds.size === 0) {
    document.getElementById('bookmarked-plans').classList.add('hidden');
    document.getElementById('empty-bookmarks').classList.remove('hidden');
    return;
  }
  document.getElementById('empty-bookmarks').classList.add('hidden');
  document.getElementById('bookmarked-plans').classList.remove('hidden');
  const bookmarkedPlans = allPlansData.filter(plan => {
    const key = `${plan.plan_id}__${plan.county}`;
    return bookmarkedPlanIds.has(key);
  });
  const container = document.getElementById('bookmarked-plans');
  container.innerHTML = '';
  bookmarkedPlans.forEach(plan => {
    container.appendChild(createPlanCard(plan));
  });
}

function createPlanCard(plan) {
  const div = document.createElement('div');
  div.className = 'plan-card p-5 mb-2 cursor-pointer relative transition';
  div.tabIndex = 0;
  div.onclick = () => openModal(plan.plan_id);
  const key = `${plan.plan_id}__${plan.county}`;
  const isBookmarked = bookmarkedPlanIds.has(key);
  const bookmarkIcon = isBookmarked ? '⭐' : '☆';
  let html = `
      <div class="bookmark-badge" onclick="toggleBookmark('${plan.plan_id}', '${plan.county}', event)" title="${isBookmarked ? 'Remove bookmark' : 'Bookmark this plan'}">${bookmarkIcon}</div>
      <h2 class="text-xl font-semibold text-gray-100 pr-10">${plan.plan_name}</h2>
      <p class="text-gray-300 text-base">${plan.plan_id} <span class="mx-2 text-gray-500">|</span> ${plan.issuer_name}</p>
      <p class="text-base text-gray-300 mt-1">
        <span class="font-medium text-teal-300">County:</span> ${plan.county}
        <span class="mx-2 text-gray-500">|</span>
        <span class="font-medium text-teal-300">Type:</span> ${plan.plan_type}
      </p>
      <div class="mt-3 text-sm space-y-1 text-gray-200">
        <p><span class="font-semibold text-teal-300">Customer Service Local:</span> ${plan.customer_service_local || 'Not listed'}</p>
        <p><span class="font-semibold text-teal-300">Customer Service Toll Free:</span> ${plan.customer_service_toll_free || 'Not listed'}</p>
        <p><span class="font-semibold text-teal-300">Customer Service TTY:</span> ${plan.customer_service_tty || 'Not listed'}</p>
      </div>
      <button
        type="button"
        onclick="setYourPlan(
          '${plan.plan_id}',
          '${String(plan.plan_name).replace(/'/g, "\\'")}',
          '${String(plan.county).replace(/'/g, "\\'")}',
          '${String(plan.plan_type).replace(/'/g, "\\'")}',
          event
        )"
        class="mt-3 inline-flex items-center px-3 py-1 rounded-full bg-gradient-to-r from-green-500 to-teal-500 text-slate-950 text-xs font-semibold shadow hover:shadow-lg">
        ✅ Set as Your Plan
      </button>
    `;
  div.innerHTML = html;
  return div;
}

async function fetchFilters() {
  const res = await fetch(`/api/filters?state=${encodeURIComponent(state)}`);
  const data = await res.json();
  const countySelect = document.getElementById("countyFilter");
  const issuerSelect = document.getElementById("issuerFilter");
  const typeSelect = document.getElementById("typeFilter");
  countySelect.innerHTML = '<option value="">All Counties</option>';
  data.counties.forEach(c => {
    let o = document.createElement("option");
    o.value = c; o.text = c;
    countySelect.appendChild(o);
  });
  issuerSelect.innerHTML = '<option value="">All Issuers</option>';
  data.issuers.forEach(i => {
    let o = document.createElement("option");
    o.value = i; o.text = i;
    issuerSelect.appendChild(o);
  });
  typeSelect.innerHTML = '<option value="">All Plan Types</option>';
  data.plan_types.forEach(p => {
    let o = document.createElement("option");
    o.value = p; o.text = p;
    typeSelect.appendChild(o);
  });
}

async function fetchPlans() {
  const county = document.getElementById("countyFilter").value;
  const issuer = document.getElementById("issuerFilter").value;
  const planType = document.getElementById("typeFilter").value;
  const search = document.getElementById("search").value;
  let url = `/api/plans?state=${encodeURIComponent(state)}&`;
  if (county) url += `county=${encodeURIComponent(county)}&`;
  if (issuer) url += `issuer=${encodeURIComponent(issuer)}&`;
  if (planType) url += `plan_type=${encodeURIComponent(planType)}&`;
  if (search) url += `search=${encodeURIComponent(search)}`;
  const res = await fetch(url);
  const plans = await res.json();
  allPlansData = plans;
  renderPlans(plans);
}

function renderPlans(plans) {
  const container = document.getElementById("plans");
  container.innerHTML = '';
  plans.forEach(plan => {
    container.appendChild(createPlanCard(plan));
  });
}

async function openModal(planId) {
  const plan = allPlansData.find(p => p.plan_id === planId);
  if (plan) {
    const history = JSON.parse(localStorage.getItem('viewerHistory') || '[]');
    const timestamp = new Date().toISOString();
    const entry = {
      plan_id: plan.plan_id,
      plan_name: plan.plan_name,
      county: plan.county,
      timestamp: timestamp
    };
    if (!history.length || history[history.length - 1].plan_id !== plan.plan_id) {
      history.push(entry);
      localStorage.setItem('viewerHistory', JSON.stringify(history));
    }
  }
  const res = await fetch(`/api/plans/${planId}/details`);
  const details = await res.json();
  document.getElementById("modalTitle").innerText = details.plan_name;
  const content = document.getElementById("modalContent");
 
  let brochureLink = '';
  if (details.brochure_url) {
    brochureLink = `<a href="${details.brochure_url}" target="_blank" class="external-link">📄 View Brochure</a>`;
  }

  let networkLink = '';
  if (details.network_url) {
    networkLink = `<a href="${details.network_url}" target="_blank" class="external-link">🔗 View Network</a>`;
  }

  let extraDataHtml = '';
  if (details.extra_data && Object.keys(details.extra_data).length > 0) {
    extraDataHtml = '<div class="modal-section"><h3 class="font-semibold text-teal-300 mb-2">Additional Information</h3>';
    for (const [key, value] of Object.entries(details.extra_data)) {
      if (value !== null && value !== '') {
        extraDataHtml += `<p class="text-sm text-gray-200"><strong>${key}:</strong> ${value}</p>`;
      }
    }
    extraDataHtml += '</div>';
  }

  content.innerHTML = `
      <div class="modal-section">
        <p class="text-gray-200"><strong class="text-teal-300">Plan ID:</strong> ${details.plan_id}</p>
        <p class="text-gray-200"><strong class="text-teal-300">Issuer:</strong> ${details.issuer_name}</p>
        <p class="text-gray-200"><strong class="text-teal-300">County:</strong> ${details.county}</p>
        <p class="text-gray-200"><strong class="text-teal-300">Plan Type:</strong> ${details.plan_type}</p>
        ${details.rating_area ? `<p class="text-gray-200"><strong class="text-teal-300">Rating Area:</strong> ${details.rating_area}</p>` : ''}
        ${details.child_only_offering ? `<p class="text-gray-200"><strong class="text-teal-300">Child Only Offering:</strong> ${details.child_only_offering}</p>` : ''}
        ${details.metal_level ? `<p class="text-gray-200"><strong class="text-teal-300">Metal Level:</strong> ${details.metal_level}</p>` : ''}
      </div>
      <div class="modal-section">
        ${brochureLink}
        ${networkLink}
      </div>
      ${extraDataHtml}
    `;
  document.getElementById("modal").classList.remove("hidden");
  document.getElementById("modal").classList.add("flex");
}

function showViewerHistory() {
  const history = JSON.parse(localStorage.getItem('viewerHistory') || '[]');
  const list = document.getElementById('history-list');
  list.innerHTML = '';
  if (history.length === 0) {
    list.innerHTML = '<li class="text-gray-500">No plans viewed yet.</li>';
  } else {
    history.slice().reverse().forEach(entry => {
      const date = new Date(entry.timestamp);
      const formatted = date.toLocaleString();
      const li = document.createElement('li');
      li.innerHTML = `<strong class="text-gray-100">${entry.plan_name}</strong> <span class="text-teal-300">(${entry.county})</span> <span class="text-gray-400 ml-2">[${formatted}]</span>`;
      list.appendChild(li);
    });
  }
  document.getElementById('history-section').classList.remove('hidden');
}

function closeModal() {
  document.getElementById("modal").classList.add("hidden");
  document.getElementById("modal").classList.remove("flex");
}

function setYourPlan(planId, planName, county, planType, event) {
  event.stopPropagation();
  const yourPlan = { plan_id: planId, plan_name: planName, county: county, plan_type: planType };
  localStorage.setItem('yourPlan', JSON.stringify(yourPlan));
  renderYourPlanPanel();
}

function clearYourPlan() {
  localStorage.removeItem('yourPlan');
  renderYourPlanPanel();
}

function renderYourPlanPanel() {
  const raw = localStorage.getItem('yourPlan');
  const emptyEl = document.getElementById('your-plan-empty');
  const contentEl = document.getElementById('your-plan-content');
  if (!emptyEl || !contentEl) return;

  if (!raw) {
    emptyEl.classList.remove('hidden');
    contentEl.classList.add('hidden');
    return;
  }

  const p = JSON.parse(raw);
  document.getElementById('your-plan-name').innerText = p.plan_name || '';
  document.getElementById('your-plan-id').innerText = p.plan_id || '';
  document.getElementById('your-plan-county').innerText = p.county || '';
  document.getElementById('your-plan-type').innerText = p.plan_type || '';
  emptyEl.classList.add('hidden');
  contentEl.classList.remove('hidden');
}

window.onload = () => {
  document.getElementById("countyFilter").onchange = fetchPlans;
  document.getElementById("issuerFilter").onchange = fetchPlans;
  document.getElementById("typeFilter").onchange = fetchPlans;
  document.getElementById("search").oninput = fetchPlans;
  fetchFilters();
  fetchPlans();
  renderYourPlanPanel();
};
