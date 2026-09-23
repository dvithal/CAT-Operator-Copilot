/**
 * Feature 6 — Advanced what-if simulation panel.
 * Shows weather + extended scenarios, reuses existing ETA model output.
 */
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { FlaskConical } from 'lucide-react'

export default function WhatIfPanel({ data }) {
  if (!data || data.error) return null

  const currentEta = data.current_eta?.predicted_time_min
  const estimate   = data.current_eta?.baseline_time_min

  // Weather scenarios
  const wxData = (data.weather_scenarios?.scenarios || []).map(s => ({
    name: s.scenario.replace('If ', ''),
    eta:  s.predicted_eta_min,
    diff: s.change_from_current_min,
  }))

  // Extended scenarios
  const extData = (data.extended_scenarios?.scenarios || []).map(s => ({
    name: s.scenario,
    eta:  s.predicted_eta_min,
    diff: s.change_from_current_min,
  }))

  return (
    <div className="card space-y-4">
      <div className="flex items-center gap-2">
        <FlaskConical size={14} className="text-purple-400" />
        <span className="section-title mb-0">What-If Scenarios</span>
      </div>

      {/* Weather */}
      {wxData.length > 0 && (
        <div>
          <div className="text-xs text-surface-100 mb-2">Weather scenarios</div>
          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={wxData} barSize={32}>
              <XAxis dataKey="name" tick={{ fill: '#718096', fontSize: 11 }} />
              <YAxis tick={{ fill: '#718096', fontSize: 11 }} unit=" min" domain={['auto', 'auto']} />
              <Tooltip
                contentStyle={{ background: '#161b24', border: '1px solid #232b3a', borderRadius: 8 }}
                formatter={(v, n) => [`${v.toFixed(1)} min`, 'Predicted ETA']}
              />
              {estimate && <ReferenceLine y={estimate} stroke="#FFCD11" strokeDasharray="4 4" label={{ value: 'Estimate', fill: '#FFCD11', fontSize: 10 }} />}
              <Bar dataKey="eta" fill="#3b82f6" radius={[4,4,0,0]}
                label={{ position: 'top', fill: '#9ca3af', fontSize: 10, formatter: v => `${v.toFixed(0)}m` }} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Extended */}
      {extData.length > 0 && (
        <div>
          <div className="text-xs text-surface-100 mb-2">Extended scenarios</div>
          <div className="space-y-2">
            {extData.map((s, i) => (
              <div key={i} className="flex items-center justify-between text-xs bg-surface-600 rounded-lg px-3 py-2">
                <span className="text-gray-300">{s.name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-cat-500 font-mono">{s.eta.toFixed(0)} min</span>
                  <span className={`font-mono text-xs ${s.diff > 0 ? 'text-red-400' : s.diff < 0 ? 'text-green-400' : 'text-surface-100'}`}>
                    {s.diff >= 0 ? '+' : ''}{s.diff.toFixed(1)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <p className="text-xs text-surface-200 italic">{data.disclaimer}</p>
    </div>
  )
}
