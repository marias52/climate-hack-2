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

const noDataRegions = [
  'Awdal',
  'Gedo',
  'Hiraan',
  'Lower Shabelle',
  'Middle Shabelle',
  'Sool',
  'Togdheer',
  'Woqooyi Galbeed'
];

const dataLayers = [
  ['forestLoss', 'Forest loss'],
  ['populationImpact', 'Population impact'],
  ['charcoalDependency', 'Charcoal dependency'],
  ['recoveryPotential', 'Recovery potential'],
  ['droughtStress', 'Drought stress']
];

const districtPositions = [
  { x: 79, y: 70 },
  { x: 78, y: 61 },
  { x: 72, y: 58 },
  { x: 70, y: 50 },
  { x: 82, y: 29 },
  { x: 77, y: 22 },
  { x: 77, y: 43 },
  { x: 74, y: 66 }
];

function App() {
  const [query, setQuery] = useState('');
  const [selectedId, setSelectedId] = useState(districts[0].id);
  const [selectedRegion, setSelectedRegion] = useState('All');
  const [activeLayers, setActiveLayers] = useState(dataLayers.map(([key]) => key));
  const [zoomed, setZoomed] = useState(false);

  const regions = useMemo(() => {
    const dataRegions = [...new Set(districts.map((district) => district.region))];
    return ['All', ...dataRegions, ...noDataRegions];
  }, []);

  const selected = districts.find((district) => district.id === selectedId) || districts[0];
  const selectedRegionHasData =
    selectedRegion === 'All' || districts.some((district) => district.region === selectedRegion);

  const visibleDistricts = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return districts.filter((district) => {
      const matchesQuery = `${district.name} ${district.region}`.toLowerCase().includes(normalized);
      const matchesRegion = selectedRegion === 'All' || district.region === selectedRegion;
      return matchesQuery && matchesRegion;
    });
  }, [query, selectedRegion]);

  function toggleLayer(layerKey) {
    setActiveLayers((layers) =>
      layers.includes(layerKey)
        ? layers.filter((key) => key !== layerKey)
        : [...layers, layerKey]
    );
  }

  function displayScore(district) {
    if (activeLayers.length === 0 || activeLayers.length === dataLayers.length) {
      return district.priorityScore;
    }
    const total = activeLayers.reduce((sum, key) => sum + district[key], 0);
    return Math.round(total / activeLayers.length);
  }

  const selectedDisplayScore = displayScore(selected);
  const selectedRisk = getRiskLevel(selectedDisplayScore);

  return (
    <main className="dashboard-shell">
      <aside className="sidebar" aria-label="District priority list">
        <div className="brand-block">
          <div className="logo-scene" aria-label="Hakad landscape logo">
            <span className="tree-canopy" />
            <span className="tree-trunk" />
            <span className="people-row" />
          </div>
          <div>
            <p className="eyebrow">Restoration intelligence</p>
            <h1>Hakad</h1>
          </div>
        </div>

        <label className="search-box">
          <span>Search district or region</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try Juba, Bay, Puntland"
          />
        </label>

        <section className="layer-panel" aria-label="Data layers">
          <div className="panel-title">
            <span>Data layers</span>
            <b>{activeLayers.length}/{dataLayers.length}</b>
          </div>
          {dataLayers.map(([key, label]) => (
            <label key={key} className="toggle-row">
              <input
                type="checkbox"
                checked={activeLayers.includes(key)}
                onChange={() => toggleLayer(key)}
              />
              <span>{label}</span>
            </label>
          ))}
        </section>

        <section className="region-panel" aria-label="Region filter">
          <div className="panel-title">
            <span>Regions</span>
            <b>{selectedRegionHasData ? 'Data' : 'No data'}</b>
          </div>
          <div className="region-chips">
            {regions.map((region) => {
              const hasData = region === 'All' || districts.some((district) => district.region === region);
              return (
                <button
                  key={region}
                  className={`${selectedRegion === region ? 'active' : ''} ${hasData ? '' : 'empty'}`}
                  onClick={() => setSelectedRegion(region)}
                >
                  {region}
                </button>
              );
            })}
          </div>
        </section>

        <div className="priority-summary">
          <span>High priority</span>
          <strong>{districts.filter((district) => displayScore(district) >= 70).length}</strong>
        </div>

        <div className="district-list">
          {!selectedRegionHasData && (
            <div className="no-data-card">
              <strong>{selectedRegion}</strong>
              <span>No data available yet</span>
            </div>
          )}

          {selectedRegionHasData && visibleDistricts.map((district) => {
            const score = displayScore(district);
            const risk = getRiskLevel(score);
            return (
              <button
                key={district.id}
                className={`district-item ${selected.id === district.id ? 'active' : ''}`}
                onClick={() => setSelectedId(district.id)}
              >
                <span>
                  <strong>{district.name}</strong>
                  <small>{district.region}</small>
                </span>
                <span className={`risk-pill ${risk.toLowerCase()}`}>{risk}</span>
                <b>{score}</b>
              </button>
            );
          })}
        </div>
      </aside>

      <section className="map-panel" aria-label="Africa and Somalia priority map">
        <header className="topbar">
          <div>
            <p className="eyebrow">Africa context map</p>
            <h2>Somalia Risk Focus</h2>
          </div>
          <div className="topbar-actions">
            <span>Somalia data only</span>
            <button type="button" onClick={() => setZoomed(true)}>Focus</button>
          </div>
        </header>

        <div className="map-stage">
          <div className={`africa-map ${zoomed ? 'zoomed' : ''}`}>
            <div className="africa-continent" aria-hidden="true" />
            <div className="somalia-outline" aria-label="Somalia risk heatmap">
              {districts.map((district, index) => {
                const score = displayScore(district);
                return (
                  <button
                    key={district.id}
                    className={`risk-cell ${getRiskLevel(score).toLowerCase()} ${selected.id === district.id ? 'selected' : ''}`}
                    style={{
                      '--x': `${districtPositions[index].x}%`,
                      '--y': `${districtPositions[index].y}%`
                    }}
                    onClick={() => setSelectedId(district.id)}
                    aria-label={`${district.name}, ${getRiskLevel(score)} risk, score ${score}`}
                  >
                    <span>{district.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="map-legend" aria-label="Risk legend">
            <span className="low">Low</span>
            <span className="medium">Medium</span>
            <span className="high">High</span>
            <span className="critical">Critical</span>
          </div>

          <div className="map-controls" aria-label="Map zoom tools">
            <button type="button" onClick={() => setZoomed(true)}>+</button>
            <button type="button" onClick={() => setZoomed(false)}>-</button>
            <button type="button" onClick={() => setZoomed((value) => !value)}>
              {zoomed ? 'AF' : 'SO'}
            </button>
          </div>

          <div className="timeline">
            <span>Africa</span>
            <div><i /></div>
            <span>Zoom to Somalia</span>
          </div>
        </div>
      </section>

      <aside className="analytics-panel" aria-label="District analytics">
        <div className="analytics-header">
          <span className={`risk-pill ${selectedRisk.toLowerCase()}`}>{selectedRisk}</span>
          <h2>{selected.name}</h2>
          <p>{selected.region} · Hakad priority assessment</p>
        </div>

        <div className="score-card">
          <span>Priority score</span>
          <strong>{selectedDisplayScore}</strong>
          <div className="score-track">
            <i style={{ width: `${selectedDisplayScore}%` }} />
          </div>
        </div>

        <section className="metrics-grid">
          {dataLayers.map(([key, label]) => (
            <article key={key} className={`metric-card ${activeLayers.includes(key) ? '' : 'muted'}`}>
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

function getRiskLevel(score) {
  if (score >= 85) return 'Critical';
  if (score >= 70) return 'High';
  if (score >= 50) return 'Medium';
  return 'Low';
}

const rootElement = document.getElementById('root');
const root = window.__hakadRoot || createRoot(rootElement);
window.__hakadRoot = root;
root.render(<App />);
