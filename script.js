const plans = [
  {
    name: 'BrightSmile Preferred',
    provider: 'Aurora Dental',
    premium: 38,
    deductible: 50,
    coverage: 80,
    network: 'PPO',
    perks: ['Orthodontics', 'Nationwide network', 'Free cleanings'],
  },
  {
    name: 'Hometown Family Plan',
    provider: 'Community Care',
    premium: 29,
    deductible: 75,
    coverage: 70,
    network: 'HMO',
    perks: ['Low copays', 'Local clinics', 'Preventative first'],
  },
  {
    name: 'FlexChoice Plus',
    provider: 'Blue Horizon',
    premium: 52,
    deductible: 0,
    coverage: 90,
    network: 'PPO',
    perks: ['Adult orthodontics', 'Implant coverage', 'Teledentistry'],
  },
  {
    name: 'Student Saver',
    provider: 'Campus Dental',
    premium: 24,
    deductible: 100,
    coverage: 60,
    network: 'EPO',
    perks: ['No waiting period', 'Night/weekend visits', 'Digital ID card'],
  },
  {
    name: 'Premium Protect',
    provider: 'BrightPath',
    premium: 68,
    deductible: 25,
    coverage: 95,
    network: 'PPO',
    perks: ['Cosmetic discounts', 'Specialist visits', 'Mouthguard included'],
  },
];

const erSamples = [
  { facility: 'Sunnyside ER', city: 'Austin', wait: 22, trend: '▲ slightly up' },
  { facility: 'Harborview Medical', city: 'Boston', wait: 14, trend: '▼ easing' },
  { facility: 'Northline Hospital', city: 'Denver', wait: 36, trend: '▲ high' },
  { facility: 'Westfield Care', city: 'Seattle', wait: 18, trend: '— steady' },
  { facility: 'Coastal General', city: 'San Diego', wait: 28, trend: '▼ improving' },
];

const planResults = document.getElementById('plan-results');
const searchInput = document.getElementById('search');
const networkSelect = document.getElementById('network');
const premiumRange = document.getElementById('premium');
const premiumValue = document.getElementById('premium-value');
const sortSelect = document.getElementById('sort');
const erList = document.getElementById('er-list');
const refreshEr = document.getElementById('refresh-er');

const formatMoney = (value) => `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

function renderPlans(items) {
  planResults.innerHTML = '';

  if (!items.length) {
    const empty = document.createElement('p');
    empty.textContent = 'No plans matched those filters. Try widening your search.';
    empty.className = 'plan-note';
    planResults.appendChild(empty);
    return;
  }

  items.forEach((plan) => {
    const card = document.createElement('article');
    card.className = 'plan-card';

    const title = document.createElement('h4');
    title.textContent = plan.name;

    const provider = document.createElement('p');
    provider.textContent = plan.provider;

    const badge = document.createElement('span');
    badge.className = 'badge';
    badge.textContent = plan.network;

    const perks = document.createElement('p');
    perks.textContent = plan.perks.join(' • ');

    const stats = document.createElement('div');
    stats.className = 'plan-stats';
    stats.innerHTML = `
      <span>${formatMoney(plan.premium)} / mo</span>
      <span>${formatMoney(plan.deductible)} deductible</span>
      <span>${plan.coverage}% preventative</span>
    `;

    card.append(title, provider, badge, perks, stats);
    planResults.appendChild(card);
  });
}

function applyFilters() {
  const searchTerm = searchInput.value.trim().toLowerCase();
  const network = networkSelect.value;
  const maxPremium = Number(premiumRange.value);
  const sortBy = sortSelect.value;

  const filtered = plans
    .filter((plan) => (network ? plan.network === network : true))
    .filter((plan) => plan.premium <= maxPremium)
    .filter((plan) => {
      if (!searchTerm) return true;
      const haystack = `${plan.name} ${plan.provider} ${plan.perks.join(' ')}`.toLowerCase();
      return haystack.includes(searchTerm);
    })
    .sort((a, b) => {
      if (sortBy === 'premium') return a.premium - b.premium;
      if (sortBy === 'deductible') return a.deductible - b.deductible;
      return b.coverage - a.coverage;
    });

  premiumValue.textContent = formatMoney(maxPremium);
  renderPlans(filtered);
}

function shuffle(array) {
  const clone = [...array];
  for (let i = clone.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [clone[i], clone[j]] = [clone[j], clone[i]];
  }
  return clone;
}

function renderEr(list) {
  erList.innerHTML = '';
  list.forEach((er) => {
    const card = document.createElement('article');
    card.className = 'er-card';

    const title = document.createElement('strong');
    title.textContent = er.facility;

    const location = document.createElement('p');
    location.textContent = er.city;

    const wait = document.createElement('p');
    wait.innerHTML = `<strong>${er.wait} min</strong> wait · ${er.trend}`;

    card.append(title, location, wait);
    erList.appendChild(card);
  });
}

searchInput.addEventListener('input', applyFilters);
networkSelect.addEventListener('change', applyFilters);
premiumRange.addEventListener('input', applyFilters);
sortSelect.addEventListener('change', applyFilters);
refreshEr.addEventListener('click', () => renderEr(shuffle(erSamples)));

premiumValue.textContent = formatMoney(Number(premiumRange.value));
renderPlans(plans);
renderEr(erSamples);
