export default function LoadingSpinner({ label = 'Loading…' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3 text-surface-100">
      <div className="w-8 h-8 border-2 border-surface-400 border-t-cat-500 rounded-full animate-spin" />
      <span className="text-sm">{label}</span>
    </div>
  )
}
