import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const districts = [
  {
    id: 'lower-juba',
    name: 'Lower Juba',
    region: 'Jubaland',
    forestLoss: 86,
    populationImpact: 72,
    charcoalDependency: 90,
    recoveryPotential: 64,
    droughtStress: 78,
    priorityScore: 88,
    riskLevel: 'Critical',
    interventionPackage: 'Mangrove restoration, charcoal alternatives, riverine patrols',
    predictedImpact: 'Protect 18,400 ha and reduce charcoal pressure by 22%'
  },
  {
    id: 'middle-juba',
    name: 'Middle Juba',
    region: 'Jubaland',
    forestLoss: 74,
    populationImpact: 64,
    charcoalDependency: 83,
    recoveryPotential: 71,
    droughtStress: 70,
    priorityScore: 81,
    riskLevel: 'High',
    interventionPackage: 'Agroforestry corridors, nursery expansion, clean cookstoves',
    predictedImpact: 'Restore 12,700 ha and improve household resilience by 18%'
  },
  {
    id: 'bay',
    name: 'Bay',
    region: 'South West',
    forestLoss: 63,
    populationImpact: 68,
    charcoalDependency: 57,
    recoveryPotential: 76,
    droughtStress: 84,
    priorityScore: 77,
    riskLevel: 'High',
    interventionPackage: 'Water harvesting, assisted natural regeneration, community rangers',
    predictedImpact: 'Recover 9,600 ha and lower drought exposure by 16%'
  },
  {
    id: 'bakool',
    name: 'Bakool',
    region: 'South West',
    forestLoss: 51,
    populationImpact: 71,
    charcoalDependency: 44,
    recoveryPotential: 69,
    droughtStress: 89,
    priorityScore: 72,
    riskLevel: 'High',
    interventionPackage: 'Drought buffers, fodder banks, soil stabilization',
    predictedImpact: 'Stabilize 7,900 ha and support 41,000 people'
  },
  {
    id: 'bari',
    name: 'Bari',
    region: 'Puntland',
    forestLoss: 42,
    populationImpact: 57,
    charcoalDependency: 61,
    recoveryPotential: 54,
    droughtStress: 66,
    priorityScore: 63,
    riskLevel: 'Medium',
    interventionPackage: 'Acacia restoration, livelihood grants, charcoal monitoring',
    predictedImpact: 'Restore 5,300 ha and cut illegal supply routes by 11%'
  },
  {
    id: 'sanaag',
    name: 'Sanaag',
    region: 'Somaliland',
    forestLoss: 47,
    populationImpact: 58,
    charcoalDependency: 52,
    recoveryPotential: 61,
    droughtStress: 72,
    priorityScore: 61,
    riskLevel: 'Medium',
    interventionPackage: 'Juniper protection, slope revegetation, grazing agreements',
    predictedImpact: 'Improve watershed cover across 4,800 ha'
  },
  {
    id: 'mudug',
    name: 'Mudug',
    region: 'Galmudug',
    forestLoss: 37,
    populationImpact: 62,
    charcoalDependency: 49,
    recoveryPotential: 57,
    droughtStress: 76,
    priorityScore: 58,
    riskLevel: 'Medium',
    interventionPackage: 'Rangeland restoration, solar cookers, erosion control',
    predictedImpact: 'Reduce land degradation risk for 32,000 residents'
  },
  {
    id: 'banadir',
    name: 'Banadir',
    region: 'Banadir',
    forestLoss: 28,
    populationImpact: 55,
    charcoalDependency: 36,
    recoveryPotential: 43,
    droughtStress: 48,
    priorityScore: 42,
    riskLevel: 'Low',
    interventionPackage: 'Urban tree canopy, waste-to-energy pilots, public awareness',
    predictedImpact: 'Increase canopy cover in 12 priority neighborhoods'
  }
];

const metricLabels = [
  ['forestLoss', 'Forest loss'],
  ['populationImpact', 'Population impact'],
  ['charcoalDependency', 'Charcoal dependency'],
  ['recoveryPotential', 'Recovery potential'],
  ['droughtStress', 'Drought stress']
];

function App() {
  const [query, setQuery] = useState('');
  const [selectedId, setSelectedId] = useState(districts[0].id);

  const filteredDistricts = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return districts;
    return districts.filter((district) =>
      `${district.name} ${district.region}`.toLowerCase().includes(normalized)
    );
  }, [query]);

  const selected = districts.find((district) => district.id === selectedId) || districts[0];

  return (
    <main className="dashboard-shell">
      <aside className="sidebar" aria-label="District priority list">
        <div className="brand-block">
          <span className="brand-mark">E</span>
          <div>
            <p className="eyebrow">EcoRestore</p>
            <h1>Somalia</h1>
          </div>
        </div>

        <label className="search-box">
          <span>Search district</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try Juba, Bay, Puntland"
          />
        </label>

        <div className="priority-summary">
          <span>Priority districts</span>
          <strong>{districts.filter((district) => district.priorityScore >= 70).length}</strong>
        </div>

        <div className="district-list">
          {filteredDistricts.map((district) => (
            <button
              key={district.id}
              className={`district-item ${selected.id === district.id ? 'active' : ''}`}
              onClick={() => setSelectedId(district.id)}
            >
              <span>
                <strong>{district.name}</strong>
                <small>{district.region}</small>
              </span>
              <b>{district.priorityScore}</b>
            </button>
          ))}
        </div>
      </aside>

      <section className="map-panel" aria-label="Somalia priority heatmap placeholder">
        <header className="topbar">
          <div>
            <p className="eyebrow">Restoration command view</p>
            <h2>Priority Heatmap</h2>
          </div>
          <div className="topbar-actions">
            <span>Mock data</span>
            <button>Export</button>
          </div>
        </header>

        <div className="map-stage">
          <div className="somalia-map" role="img" aria-label="Stylized Somalia heatmap">
            {districts.map((district, index) => (
              <button
                key={district.id}
                className={`heat-point ${selected.id === district.id ? 'selected' : ''}`}
                style={{
                  '--x': `${districtPositions[index].x}%`,
                  '--y': `${districtPositions[index].y}%`,
                  '--score': district.priorityScore
                }}
                onClick={() => setSelectedId(district.id)}
                aria-label={`${district.name}, priority score ${district.priorityScore}`}
              >
                <span>{district.name}</span>
              </button>
            ))}
          </div>

          <div className="map-controls" aria-label="Map tools">
            <button>+</button>
            <button>-</button>
            <button>◎</button>
          </div>

          <div className="timeline">
            <span>2022</span>
            <div><i /></div>
            <span>2026 forecast</span>
          </div>
        </div>
      </section>

      <aside className="analytics-panel" aria-label="District analytics">
        <div className="analytics-header">
          <span className={`risk-pill ${selected.riskLevel.toLowerCase()}`}>{selected.riskLevel}</span>
          <h2>{selected.name}</h2>
          <p>{selected.region}</p>
        </div>

        <div className="score-card">
          <span>Priority score</span>
          <strong>{selected.priorityScore}</strong>
          <div className="score-track">
            <i style={{ width: `${selected.priorityScore}%` }} />
          </div>
        </div>

        <section className="metrics-grid">
          {metricLabels.map(([key, label]) => (
            <article key={key} className="metric-card">
              <span>{label}</span>
              <strong>{selected[key]}%</strong>
              <div>
                <i style={{ width: `${selected[key]}%` }} />
              </div>
            </article>
          ))}
        </section>

        <section className="recommendation">
          <p className="eyebrow">Intervention recommendation</p>
          <h3>{selected.interventionPackage}</h3>
        </section>

        <section className="impact-card">
          <p className="eyebrow">Predicted impact</p>
          <h3>{selected.predictedImpact}</h3>
        </section>
      </aside>
    </main>
  );
}

const districtPositions = [
  { x: 42, y: 78 },
  { x: 45, y: 64 },
  { x: 35, y: 57 },
  { x: 31, y: 46 },
  { x: 64, y: 27 },
  { x: 54, y: 18 },
  { x: 49, y: 39 },
  { x: 39, y: 69 }
];

createRoot(document.getElementById('root')).render(<App />);
