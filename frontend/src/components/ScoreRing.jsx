export default function ScoreRing({ score = 0, size = 80, label, colorClass }) {
  const r = (size / 2) - 8
  const circ = 2 * Math.PI * r
  const filled = (score / 100) * circ
  const color = colorClass || (score >= 85 ? '#22c55e' : score >= 70 ? '#f59e0b' : score >= 50 ? '#f97316' : '#ef4444')

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#232b3a" strokeWidth="6" />
        <circle
          cx={size/2} cy={size/2} r={r}
          fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={`${filled} ${circ - filled}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${size/2} ${size/2})`}
        />
        <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle"
          fill="white" fontSize={size * 0.22} fontWeight="600">
          {score}
        </text>
      </svg>
      {label && <span className="text-xs text-surface-100">{label}</span>}
    </div>
  )
}
