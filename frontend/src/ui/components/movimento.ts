export function prefereMenosMovimento(): boolean {
  if (typeof matchMedia !== 'function') return true
  return matchMedia('(prefers-reduced-motion: reduce)').matches
}
