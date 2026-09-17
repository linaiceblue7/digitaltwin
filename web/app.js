let map, markers = [], allData = [];

fetch('data.json')
  .then(r => r.json())
  .then(data => {
    allData = data;
    initKPI(data);
    initMap(data);
    initTable(data);
    initControls();
  })
  .catch(err => console.error('Ошибка загрузки data.json:', err));

function initKPI(data) {
  const avgNpv = data.reduce((s, d) => s + d.npv, 0) / data.length;
  const avgIrr = data.reduce((s, d) => s + d.irr, 0) / data.length;
  const avgPayback = data.reduce((s, d) => s + d.payback_years, 0) / data.length;
  const totalCapex = data.reduce((s, d) => s + d.capex, 0);
  const avgPower = data.reduce((s, d) => s + d.power_kw, 0) / data.length;

  const kpis = [
    { num: '01', label: 'Приоритетных локаций', value: data.length, suffix: '', sub: 'по результатам оптимизации', decimals: 0 },
    { num: '02', label: 'Средняя мощность', value: avgPower, suffix: ' кВт', sub: 'на одну станцию', decimals: 0 },
    { num: '03', label: 'Средний NPV', value: avgNpv / 1e6, suffix: ' млн ₽', sub: 'за 10 лет, дисконт 12%', decimals: 1 },
    { num: '04', label: 'Средний IRR', value: avgIrr * 100, suffix: '%', sub: 'внутренняя норма доходности', decimals: 0 },
    { num: '05', label: 'Окупаемость', value: avgPayback, suffix: ' лет', sub: 'средний срок возврата', decimals: 1 },
    { num: '06', label: 'Суммарный CAPEX', value: totalCapex / 1e6, suffix: ' млн ₽', sub: 'инвестиции в топ-20', decimals: 0 }
  ];

  document.getElementById('kpiGrid').innerHTML = kpis.map(k => `
    <div class="glass-card">
      <div class="kpi-icon">${k.num}</div>
      <div class="kpi-label">${k.label}</div>
      <div class="kpi-value" data-target="${k.value}" data-suffix="${k.suffix}" data-decimals="${k.decimals}">0</div>
      <div class="kpi-sub">${k.sub}</div>
    </div>
  `).join('');

  document.querySelectorAll('.kpi-value').forEach(el => {
    const target = parseFloat(el.dataset.target);
    const suffix = el.dataset.suffix || '';
    const decimals = parseInt(el.dataset.decimals) || 0;
    animateCounter(el, target, suffix, decimals);
  });
}

function animateCounter(el, target, suffix, decimals) {
  const duration = 1400;
  const start = performance.now();
  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = (target * eased).toFixed(decimals) + suffix;
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function initMap(data) {
  map = L.map('map', { zoomControl: true, attributionControl: false }).setView([55.7558, 37.6173], 10);

  // Светлые тайлы OpenStreetMap без ключа и водяных знаков
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
  }).addTo(map);

  renderMarkers(data);
}

function renderMarkers(data) {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  data.forEach(d => {
    const color = d.power_kw >= 350 ? '#EF4444' : d.power_kw >= 150 ? '#F59E0B' : '#10B981';
    const radius = d.power_kw >= 350 ? 11 : d.power_kw >= 150 ? 9 : 7;
    const marker = L.circleMarker([d.latitude, d.longitude], {
      radius, fillColor: color, color: '#fff', weight: 2.5, opacity: 1, fillOpacity: 0.9
    }).addTo(map);
    marker.bindPopup(`
      <div class="popup-title">Локация №${d.priority}</div>
      <div class="popup-row"><span>Мощность:</span><span>${d.power_kw} кВт</span></div>
      <div class="popup-row"><span>Прогноз спроса:</span><span>${d.predicted_demand_kwh} кВт·ч</span></div>
      <div class="popup-row"><span>CAPEX:</span><span>${(d.capex / 1e6).toFixed(1)} млн ₽</span></div>
      <div class="popup-row"><span>NPV:</span><span>${(d.npv / 1e6).toFixed(1)} млн ₽</span></div>
      <div class="popup-row"><span>IRR:</span><span>${(d.irr * 100).toFixed(0)}%</span></div>
      <div class="popup-row"><span>Окупаемость:</span><span>${d.payback_years} лет</span></div>
    `);
    markers.push(marker);
  });
}

function initTable(data) {
  document.querySelector('#locTable tbody').innerHTML = data.map(d => {
    const npvClass = d.npv > 30000000 ? 'good' : d.npv > 15000000 ? '' : 'warn';
    const payClass = d.payback_years <= 3 ? 'good' : d.payback_years <= 5 ? '' : 'warn';
    return `<tr>
      <td class="priority">${d.priority}</td>
      <td>${d.power_kw} кВт</td>
      <td>${d.predicted_demand_kwh} кВт·ч</td>
      <td>${(d.capex / 1e6).toFixed(1)} млн ₽</td>
      <td class="${npvClass}">${(d.npv / 1e6).toFixed(1)} млн ₽</td>
      <td>${(d.irr * 100).toFixed(0)}%</td>
      <td class="${payClass}">${d.payback_years} лет</td>
    </tr>`;
  }).join('');
}

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
  const filtered = allData.filter(d => d.power_kw >= minPower).slice(0, topN);
  renderMarkers(filtered);
  initTable(filtered);
}