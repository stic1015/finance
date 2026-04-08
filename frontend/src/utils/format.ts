export function formatPercent(value: number) {
  return `${value >= 0 ? '+' : ''}${(value * 100).toFixed(2)}%`
}

export function formatMarketPercent(value: number) {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
}

export function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value)
}

export function compactNumber(value: number) {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: 2,
  }).format(value)
}
