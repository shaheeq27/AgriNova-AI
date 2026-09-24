export function parseDateString(dateString: string | null | undefined): Date | null {
  if (!dateString) return null;
  // If it's YYYY-MM-DD, parse it as local time to prevent UTC shift
  const ymdRegex = /^(\d{4})-(\d{2})-(\d{2})(?:T.*)?$/;
  const match = dateString.match(ymdRegex);
  if (match) {
    const year = parseInt(match[1], 10);
    const month = parseInt(match[2], 10) - 1; // months are 0-indexed
    const day = parseInt(match[3], 10);
    return new Date(year, month, day);
  }
  const parsed = new Date(dateString);
  return isNaN(parsed.getTime()) ? null : parsed;
}

export function formatDateShort(date: Date | null): string {
  if (!date) return "Date unavailable";
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
