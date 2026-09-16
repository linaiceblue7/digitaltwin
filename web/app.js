let map, markers = [], allData = [];

// Загрузка данных
fetch('data.json')
  .then(r => r.json())
  .then(data => {
    allData = data;
    initKPI(data);
    initMap(data);
    initTable(data);
    initControls();
  })
  .catch(err => {
    console.error('Ошибка загрузки data.json:', err);
    alert('Не удалось загрузить data.json. Убедитесь, что файл рядом с index.html.');
  });

// KPI
function initKPI(data) {
  const avgNpv = data.reduce((s, d) => s + d.npv, 0) / data.length;
  const avgIrr = data.reduce((s, d) => s + d.irr, 0) / data.length;
  const avgPayback = data.reduce((s, d) => s + d.payback_years, 0) / data.length;
  const totalCapex = data.reduce((s, d) => s + d.capex, 0);
  const avgPower = data.reduce((s, d) => s + d.power_kw, 0) / data.length;

  const kpis = [
    { icon: '📍', label: 'Приоритетных локаций', value: data.length, sub: 'по результатам оптимизации' },
    { icon: '⚡', label: 'Средняя мощность', value: avgPower.toFixed(0) + ' кВт', sub: 'на одну станцию' },
    { icon: '💰', label: 'Средний NPV', value: (avgNpv / 1e6).toFixed(1) + ' млн ₽', sub: 'за 10 лет, дисконт 12%' },
    { icon: '📈', label: 'Средний IRR', value: (avgIrr * 100).toFixed(0) + '%', sub: 'внутренняя норма доходности' },
    { icon: '⏱', label: 'Окупаемость', value: avgPayback.toFixed(1) + ' лет', sub: 'средний срок возврата' },
    { icon: '💎', label: 'Суммарный CAPEX', value: (totalCapex / 1e6).toFixed(0) + ' млн ₽', sub: 'инвестиции в топ-20' }
  ];

  document.getElementById('kpiGrid').innerHTML = kpis.map(k => `
    <div class="kpi-card">
      <div class="kpi-icon">${k.icon}</div>
      <div class="kpi-label">${k.label}</div>
      <div class="kpi-value">${k.value}</div>
      <div class="kpi-sub">${k.sub}</div>
    </div>
  `).join('');
}

// Карта
function initMap(data) {
  map = L.map('map', {
    zoomControl: true,
    attributionControl: false
  }).setView([55.7558, 37.6173], 10);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(map);

  renderMarkers(data);
}

function renderMarkers(data) {
  markers.forEach(m => map.removeLayer(m));
  markers = [];

  data.forEach(d => {
    const color = d.power_kw >= 350 ? '#ef4444' : d.power_kw >= 150 ? '#f59e0b' : '#10b981';
    const radius = d.power_kw >= 350 ? 11 : d.power_kw >= 150 ? 9 : 7;

    const marker = L.circleMarker([d.latitude, d.longitude], {
      radius: radius,
      fillColor: color,
      color: color,
      weight: 2,
      opacity: 0.4,
      fillOpacity: 0.85
    }).addTo(map);

    marker.bindPopup(`
      <div class="popup-title">Локация №${d.priority}</div>
      <div class="popup-row"><span>Мощность:</span><span>${d.power_kw} кВт</span></div>
      <div class="popup-row"><span>Спрос:</span><span>${d.predicted_demand_kwh} кВт·ч</span></div>
      <div class="popup-row"><span>CAPEX:</span><span>${(d.capex / 1e6).toFixed(1)} млн ₽</span></div>
      <div class="popup-row"><span>NPV:</span><span>${(d.npv / 1e6).toFixed(1)} млн ₽</span></div>
      <div class="popup-row"><span>IRR:</span><span>${(d.irr * 100).toFixed(0)}%</span></div>
      <div class="popup-row"><span>Окупаемость:</span><span>${d.payback_years} лет</span></div>
    `);

    markers.push(marker);
  });
}

// Таблица
function initTable(data) {
  document.querySelector('#locTable tbody').innerHTML = data.map(d => {
    const npvClass = d.npv > 30000000 ? 'good' : d.npv > 15000000 ? '' : 'warn';
    const payClass = d.payback_years <= 3 ? 'good' : d.payback_years <= 5 ? '' : 'warn';
    return `
      <tr>
        <td class="priority">${d.priority}</td>
        <td>${d.power_kw} кВт</td>
        <td>${d.predicted_demand_kwh} кВт·ч</td>
        <td>${(d.capex / 1e6).toFixed(1)} млн ₽</td>
        <td class="${npvClass}">${(d.npv / 1e6).toFixed(1)} млн ₽</td>
        <td>${(d.irr * 100).toFixed(0)}%</td>
        <td class="${payClass}">${d.payback_years} лет</td>
      </tr>
    `;
  }).join('');
}

// Фильтры
function initControls() {
  document.getElementById('powerFilter').addEventListener('change', applyFilters);
  document.getElementById('topFilter').addEventListener('input', e => {
    document.getElementById('topValue').textContent = e.target.value;
    applyFilters();
  });
}

function applyFilters() {
  const minPower = parseInt(document.getElementById('powerFilter').value);
  const topN = parseInt(document.getElementById('topFilter').value);

  const filtered = allData
    .filter(d => d.power_kw >= minPower)
    .slice(0, topN);

  renderMarkers(filtered);
  initTable(filtered);
}