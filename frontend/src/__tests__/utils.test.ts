import { formatPercent, formatINR } from '../lib/utils';

describe('Metrics Formatting (utils.ts)', () => {
  describe('formatPercent', () => {
    it('formats numeric value correctly', () => {
      expect(formatPercent(0.752)).toBe('75.2%');
      expect(formatPercent(1.0)).toBe('100.0%');
    });

    it('formats zero correctly', () => {
      expect(formatPercent(0)).toBe('0.0%');
    });

    it('returns N/A for null', () => {
      expect(formatPercent(null as any)).toBe('N/A');
    });

    it('returns N/A for undefined', () => {
      expect(formatPercent(undefined as any)).toBe('N/A');
    });

    it('returns N/A for NaN', () => {
      expect(formatPercent(NaN)).toBe('N/A');
    });
  });

  describe('formatINR', () => {
    it('formats real variance to real value', () => {
      expect(formatINR(5000)).toMatch(/5,000/);
    });

    it('formats zero variance to zero', () => {
      expect(formatINR(0)).toMatch(/0/);
    });

    it('displays "—" for missing variance (null/undefined)', () => {
      expect(formatINR(null as any)).toBe('—');
      expect(formatINR(undefined as any)).toBe('—');
      expect(formatINR(NaN)).toBe('—');
    });
  });
});
