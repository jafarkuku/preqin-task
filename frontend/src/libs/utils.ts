export const formatCurrency = (amount: number): string => {
  if (amount >= 1000000000) {
    return `£${(amount / 1000000000).toFixed(1)}B`;
  } else if (amount >= 1000000) {
    return `£${(amount / 1000000).toFixed(0)}M`;
  } else if (amount >= 1000) {
    return `£${(amount / 1000).toFixed(0)}K`;
  } else {
    return `£${amount.toLocaleString()}`;
  }
};

export function capitalizeWords(phrase: string): string {
  return phrase
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}