/**
 * FENlife analitik yardımcı fonksiyonları.
 * Backend features/ modülüyle senkron algoritmalar (trend, risk, ders ort.).
 * Algoritma değişirse hem burası hem backend/app/features/ güncellenmelidir.
 */
import type { Exam, RiskResult, SubjectAverage, TrendResult } from '@/lib/types';
import { SUBJECT_META } from '@/lib/types';

/** Puan serisinin lineer trend'ini hesaplar (numpy.polyfit eşdeğeri). */
export function computeTrend(exams: Exam[]): TrendResult {
  if (exams.length < 2) return { slope: 0, delta: 0, direction: 'flat' };

  const n = exams.length;
  const xs = exams.map((_, i) => i);
  const ys = exams.map((e) => e.puan);

  const xMean = xs.reduce((a, b) => a + b, 0) / n;
  const yMean = ys.reduce((a, b) => a + b, 0) / n;
  const num = xs.reduce((acc, x, i) => acc + (x - xMean) * (ys[i] - yMean), 0);
  const den = xs.reduce((acc, x) => acc + Math.pow(x - xMean, 2), 0);
  const slope = den === 0 ? 0 : num / den;
  const delta = ys[n - 1] - ys[0];
  const direction: TrendResult['direction'] =
    slope > 2 ? 'up' : slope < -2 ? 'down' : 'flat';

  return { slope, delta, direction };
}

/** Kural tabanlı risk sınıflandırması. */
export function computeRisk(avgPuan: number, exams: Exam[]): RiskResult {
  if (exams.length < 5) {
    return { level: 'sinirli', label: 'Sınırlı Analiz', color: '#737373' };
  }

  const { direction } = computeTrend(exams);
  const last = exams[exams.length - 1].puan;
  let score = 0;

  if (avgPuan < 320) score += 2;
  else if (avgPuan < 370) score += 1;

  if (direction === 'down') score += 2;
  else if (direction === 'flat') score += 1;

  if (last < avgPuan - 30) score += 1;

  if (score >= 4) return { level: 'yuksek', label: 'Yüksek Öncelikli', color: '#B91C1C' };
  if (score >= 2) return { level: 'orta',   label: 'Orta Öncelikli',   color: '#CA8A04' };
  return              { level: 'dusuk',  label: 'Stabil Gelişim',   color: '#15803D' };
}

/** Ders bazlı istatistikler (avg, max, min, son, %). */
export function computeSubjectAverages(exams: Exam[]): SubjectAverage[] {
  return SUBJECT_META.map((s) => {
    const vals = exams
      .map((e) => e[s.key as keyof Exam] as number)
      .filter((v) => v !== undefined && v !== null);

    const avg = vals.reduce((a, b) => a + b, 0) / (vals.length || 1);
    return {
      ...s,
      avg,
      max: vals.length > 0 ? Math.max(...vals) : 0,
      min: vals.length > 0 ? Math.min(...vals) : 0,
      last: vals[vals.length - 1] ?? 0,
      pct: (avg / s.qCount) * 100,
    };
  });
}

/** "dd.mm.yy" formatına dönüştür. */
export function formatDate(iso: string): string {
  const [y, m, d] = iso.split('-');
  return `${d}.${m}.${y.slice(2)}`;
}
