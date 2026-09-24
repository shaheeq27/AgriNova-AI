'use client';

import React, { useEffect, useState } from 'react';
import { farmAPI, weatherAPI, FarmData, WeatherResponse } from '@/lib/api';
import WeatherCard from '@/components/cards/WeatherCard';
import { PremiumLoader } from '@/components/ui/PremiumLoader';
import { CloudRain, AlertTriangle, Wind, Sun, Calendar } from 'lucide-react';

export default function WeatherPage() {
  const [farms, setFarms] = useState<FarmData[]>([]);
  const [weatherData, setWeatherData] = useState<Record<string, WeatherResponse | null>>({});
  const [weatherErrors, setWeatherErrors] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [selectedFarmId, setSelectedFarmId] = useState<string | null>(null);

  useEffect(() => {
    async function loadFarmsAndWeather() {
      try {
        const res = await farmAPI.list();
        const userFarms = res.farms || [];
        setFarms(userFarms);

        if (userFarms.length > 0) {
          setSelectedFarmId(userFarms[0].id);

          const wData: Record<string, WeatherResponse | null> = {};
          const wErrors: Record<string, boolean> = {};

          const locationMap = new Map<string, string>();

          const promises = userFarms.map(async (farm) => {
            const signature = `${farm.latitude},${farm.longitude},${farm.location_city}`;
            if (locationMap.has(signature)) {
              return;
            }
            locationMap.set(signature, farm.id);
            try {
              const data = await weatherAPI.getFarmWeather(farm.id);
              wData[farm.id] = data;
            } catch (e) {
              wErrors[farm.id] = true;
            }
          });

          await Promise.all(promises);

          userFarms.forEach(farm => {
             const signature = `${farm.latitude},${farm.longitude},${farm.location_city}`;
             const masterId = locationMap.get(signature);
             if (masterId && masterId !== farm.id) {
                if (wData[masterId]) wData[farm.id] = wData[masterId];
                if (wErrors[masterId]) wErrors[farm.id] = true;
             }
          });

          setWeatherData(wData);
          setWeatherErrors(wErrors);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    loadFarmsAndWeather();
  }, []);

  if (loading) {
    return <PremiumLoader message="Syncing atmospheric data..." />;
  }

  const gridColumnsCount = Math.min(farms.length, 3);

  return (
    <div className="weather-container">
      <style dangerouslySetInnerHTML={{__html: `
        .weather-container {
          max-width: 1400px;
          margin: 0 auto;
          width: 100%;
          padding: 0 32px;
          box-sizing: border-box;
          padding-bottom: 60px;
        }

        @media (max-width: 1024px) {
          .weather-container {
            padding: 0 20px;
          }
        }

        @media (max-width: 768px) {
          .weather-container {
            padding: 0 16px;
          }
        }

        .weather-header-title {
          font-size: 40px;
          font-weight: 700;
          line-height: 1.1;
          color: #ffffff;
          margin-bottom: 8px;
        }
        .weather-header-title span {
          color: var(--accent-primary, #adff00);
        }
        .weather-header-subtitle {
          color: var(--text-muted);
          font-size: 16px;
          margin-bottom: 32px;
        }

        @media (max-width: 1024px) {
          .weather-header-title { font-size: 32px; }
        }
        @media (max-width: 768px) {
          .weather-header-title { font-size: 28px; }
        }

        .farm-grid {
          display: grid;
          gap: 20px;
        }
        .farm-grid[data-count="1"] {
          grid-template-columns: minmax(auto, 420px);
        }
        .farm-grid[data-count="2"] {
          grid-template-columns: repeat(2, minmax(auto, 420px));
        }
        .farm-grid[data-count="3"] {
          grid-template-columns: repeat(3, minmax(auto, 420px));
        }

        @media (max-width: 1024px) {
          .farm-grid[data-count="3"] {
            grid-template-columns: repeat(2, minmax(auto, 420px));
          }
        }
        @media (max-width: 768px) {
          .farm-grid[data-count="1"],
          .farm-grid[data-count="2"],
          .farm-grid[data-count="3"] {
            grid-template-columns: 1fr;
            max-width: 420px;
          }
        }

        .forecast-card-wrap {
          display: flex;
          overflow-x: auto;
          gap: 12px;
          scrollbar-width: thin;
          scrollbar-color: var(--accent-primary) transparent;
          padding-bottom: 8px;
        }
      `}} />

      <div className="animate-fade-in-up">
        <h1 className="weather-header-title">
          Weather <span>Intelligence</span>
        </h1>
        <p className="weather-header-subtitle">Forecast, alerts, and climate data for your farms</p>
      </div>

      {farms.length === 0 ? (
        <div className="animate-fade-in-up delay-1" style={{
          padding: "60px", textAlign: "center", borderRadius: "18px",
          background: "radial-gradient(ellipse at center, rgba(59,130,246,0.08), var(--surface-glass))",
          border: "1px solid rgba(255,255,255,0.05)"
        }}>
          <h2 style={{ fontSize: "24px", fontWeight: 700, marginBottom: "8px", color: '#e8f5ec' }}>No farms registered yet</h2>
          <p style={{ color: "var(--text-muted)", maxWidth: "450px", margin: "0 auto" }}>
            Weather intelligence becomes available after you register a farm. Please add a farm to view detailed forecasts and smart alerts.
          </p>
        </div>
      ) : (
        <>
          {/* Your Farms Section */}
          <div className="animate-fade-in-up delay-1">
            <h2 style={{ fontSize: "28px", fontWeight: 700, marginBottom: "16px", color: '#e8f5ec' }}>Your Farms</h2>
            <div className="farm-grid" data-count={gridColumnsCount}>
              {farms.map(farm => {
                const loc = farm.location_state ? `${farm.location_city}, ${farm.location_state}` : farm.location_city;
                return (
                  <WeatherCard
                    key={farm.id}
                    farmName={farm.name}
                    location={loc}
                    current={weatherData[farm.id]?.current || null}
                    error={weatherErrors[farm.id]}
                    selected={selectedFarmId === farm.id}
                    onClick={() => setSelectedFarmId(farm.id)}
                  />
                );
              })}
            </div>
          </div>

          {/* Details Section */}
          {selectedFarmId && (
            <div className="animate-fade-in-up delay-2" style={{ marginTop: "32px" }}>
              <h2 style={{ fontSize: "26px", fontWeight: 700, marginBottom: "16px", color: '#e8f5ec' }}>
                {farms.find(f => f.id === selectedFarmId)?.name} — Weather Details
              </h2>

              {!weatherData[selectedFarmId] && !weatherErrors[selectedFarmId] && (
                <PremiumLoader message="Loading details..." />
              )}

              {weatherErrors[selectedFarmId] && (
                <div style={{
                  padding: "32px", textAlign: "center", color: "var(--error, #ef4444)",
                  background: 'var(--surface-glass)', borderRadius: '18px', border: '1px solid rgba(255,255,255,0.05)'
                }}>
                  Weather details unavailable for this location.
                </div>
              )}

              {weatherData[selectedFarmId] && (
                <div>
                  {/* Forecast Container */}
                  <div style={{
                    width: '100%', padding: '24px', borderRadius: '18px',
                    background: 'var(--surface-glass)', border: '1px solid rgba(255,255,255,0.05)',
                    boxSizing: 'border-box'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '18px' }}>
                      <Calendar size={20} style={{ color: 'var(--accent-primary, #4ee86a)' }} />
                      <h3 style={{ fontSize: '22px', fontWeight: 700, color: '#e8f5ec' }}>7-Day Forecast</h3>
                    </div>

                    <div className="forecast-card-wrap">
                      {weatherData[selectedFarmId]?.forecast.map((day, idx) => {
                        const dateObj = new Date(day.date);
                        const dayName = idx === 0 ? 'Today' : dateObj.toLocaleDateString('en-US', { weekday: 'short' });
                        const iconColor = day.precipitation > 0 ? '#93c5fd' : 'var(--accent-primary, #4ee86a)';
                        return (
                          <div key={idx} style={{
                            flex: 1,
                            minWidth: '120px',
                            height: '170px',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: 'rgba(255,255,255,0.03)',
                            borderRadius: '12px',
                            border: '1px solid rgba(255,255,255,0.05)',
                            boxSizing: 'border-box'
                          }}>
                            <div style={{ color: 'var(--text-muted)', fontSize: '14px', marginBottom: '12px', fontWeight: 500 }}>{dayName}</div>
                            <div style={{ marginBottom: '12px', color: iconColor }}>
                              {day.precipitation > 0 ? <CloudRain size={28} /> : <Sun size={28} />}
                            </div>
                            <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', fontSize: '16px', color: '#e8f5ec', marginBottom: '12px' }}>
                              {Math.round(day.temp_max)}°<span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>/{Math.round(day.temp_min)}°</span>
                            </div>

                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                               {day.precipitation > 0 && (
                                 <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: '#93c5fd' }}>
                                   <CloudRain size={12} /> {day.precipitation}mm
                                 </div>
                               )}
                               <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: '#cbd5e1' }}>
                                 <Wind size={12} /> {Math.round(day.wind_speed)}km/h
                               </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Alerts Container */}
                  <div style={{ marginTop: '32px' }}>
                    {weatherData[selectedFarmId]?.alerts && weatherData[selectedFarmId]!.alerts.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <h3 style={{ fontSize: '22px', fontWeight: 700, color: '#e8f5ec', marginBottom: '8px' }}>Weather Alerts</h3>
                        {weatherData[selectedFarmId]!.alerts.map((alert, idx) => {
                          const isCritical = alert.severity === 'critical';
                          const color = isCritical ? '#ef4444' : '#f59e0b';
                          const bgColor = isCritical ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)';
                          return (
                            <div key={idx} style={{
                              display: 'flex',
                              alignItems: 'flex-start',
                              gap: '16px',
                              padding: '16px',
                              borderRadius: '12px',
                              background: bgColor,
                              border: `1px solid ${color}40`
                            }}>
                              <AlertTriangle size={20} style={{ color, flexShrink: 0, marginTop: '2px' }} />
                              <div>
                                <div style={{ color, fontWeight: 600, textTransform: 'capitalize', marginBottom: '4px', fontSize: '15px' }}>
                                  {alert.severity} • {alert.type}
                                </div>
                                <div style={{ color: 'var(--text-primary)', fontSize: '14px', marginBottom: '4px' }}>
                                  {alert.message}
                                </div>
                                <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                                  For {new Date(alert.date).toLocaleDateString()}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div style={{
                        padding: '24px', display: 'flex', alignItems: 'center', gap: '12px',
                        background: 'var(--surface-glass)', borderRadius: '18px', border: '1px solid rgba(255,255,255,0.05)'
                      }}>
                        <div style={{ color: 'var(--accent-primary)' }}>
                          <Sun size={24} />
                        </div>
                        <div>
                          <div style={{ color: '#e8f5ec', fontWeight: 500, fontSize: '15px' }}>No active weather alerts</div>
                          <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Conditions are safe for farming activities.</div>
                        </div>
                      </div>
                    )}
                  </div>

                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
