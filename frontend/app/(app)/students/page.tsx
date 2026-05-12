'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Users, TrendingUp, TrendingDown, Minus, FileUp, Search } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { RiskBadge } from '@/components/dashboard/shared/RiskBadge';
import type { RiskLevel } from '@/lib/types';

interface StudentRow {
  job_id: string;
  student_name: string;
  student_grade: string;
  avg_puan: number | null;
  risk_level: string | null;
  trend_direction: 'up' | 'down' | 'flat' | null;
  exam_count: number | null;
  created_at: string | null;
}

function riskResult(level: string | null) {
  const map: Record<string, { level: RiskLevel; label: string; color: string }> = {
    dusuk:   { level: 'dusuk',   label: 'Düşük Risk',  color: '#15803D' },
    orta:    { level: 'orta',    label: 'Orta Risk',   color: '#D97706' },
    yuksek:  { level: 'yuksek',  label: 'Yüksek Risk', color: '#DC2626' },
    sinirli: { level: 'sinirli', label: 'Sınırlı',     color: '#6B7280' },
  };
  return level ? (map[level] ?? map['sinirli']) : null;
}

function TrendIcon({ direction }: { direction: string | null }) {
  if (direction === 'up')   return <TrendingUp size={16} className="text-green-600" />;
  if (direction === 'down') return <TrendingDown size={16} className="text-red-600" />;
  return <Minus size={16} className="text-stone-400" />;
}

function isValidStudent(s: StudentRow): boolean {
  if (!s.student_name || s.student_name.trim() === '') return false;
  if ((s.exam_count ?? 0) <= 0) return false;
  return true;
}

function deduplicateStudents(rows: StudentRow[]): StudentRow[] {
  const map = new Map<string, StudentRow>();
  for (const s of rows) {
    const key = `${s.student_name.trim().toLowerCase()}|${s.student_grade.trim().toLowerCase()}`;
    const existing = map.get(key);
    if (!existing || (s.created_at ?? '') > (existing.created_at ?? '')) {
      map.set(key, s);
    }
  }
  return Array.from(map.values());
}

const RISK_OPTIONS = [
  { value: 'all',     label: 'Tüm Risk Seviyeleri' },
  { value: 'dusuk',   label: 'Düşük Risk'          },
  { value: 'orta',    label: 'Orta Risk'            },
  { value: 'yuksek',  label: 'Yüksek Risk'          },
  { value: 'sinirli', label: 'Sınırlı Veri'         },
];

export default function StudentsPage() {
  const router = useRouter();
  const [students, setStudents] = useState<StudentRow[]>([]);
  const [rawCount, setRawCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const [searchQuery, setSearchQuery] = useState('');
  const [gradeFilter, setGradeFilter] = useState('all');
  const [riskFilter, setRiskFilter]   = useState('all');

  useEffect(() => {
    apiClient.listStudents()
      .then((res) => {
        const raw = (res as { students: StudentRow[] }).students;
        const valid = raw.filter(isValidStudent);
        setRawCount(valid.length);
        setStudents(deduplicateStudents(valid));
      })
      .catch(() => setStudents([]))
      .finally(() => setLoading(false));
  }, []);

  const gradeOptions = useMemo(() => {
    const grades = Array.from(new Set(students.map((s) => s.student_grade).filter(Boolean))).sort();
    return grades;
  }, [students]);

  const filteredStudents = useMemo(() => {
    return students.filter((s) => {
      if (searchQuery && !s.student_name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      if (gradeFilter !== 'all' && s.student_grade !== gradeFilter) return false;
      if (riskFilter !== 'all' && s.risk_level !== riskFilter) return false;
      return true;
    });
  }, [students, searchQuery, gradeFilter, riskFilter]);

  const hasActiveFilter = searchQuery !== '' || gradeFilter !== 'all' || riskFilter !== 'all';

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Users size={22} className="text-fenlife-blue" />
            <h1 className="font-serif text-2xl font-bold text-stone-900">Öğrenciler</h1>
          </div>
          <p className="text-sm text-stone-500">
            Raporu tamamlanmış öğrenciler
            {rawCount > students.length && (
              <span className="ml-1 text-stone-400">
                ({rawCount} rapor → {students.length} tekil öğrenci)
              </span>
            )}
          </p>
        </div>
        <Link
          href="/reports/generate"
          className="inline-flex items-center gap-2 px-4 py-2 bg-fenlife-blue text-white text-sm font-semibold rounded-md hover:bg-fenlife-blue-dark transition-colors"
        >
          <FileUp size={15} />
          Yeni Rapor
        </Link>
      </div>

      {loading && (
        <div className="text-sm text-stone-500 py-12 text-center">Yükleniyor…</div>
      )}

      {!loading && students.length === 0 && (
        <div className="py-16 text-center border border-dashed border-stone-300 rounded-lg">
          <Users size={40} className="mx-auto text-stone-300 mb-3" />
          <p className="text-stone-500 font-medium">Henüz öğrenci kaydı yok</p>
          <p className="text-sm text-stone-400 mt-1 mb-5">
            Rapor Üret sayfasından sınav PDF&apos;lerini yükleyin.
          </p>
          <Link
            href="/reports/generate"
            className="inline-flex items-center gap-2 px-4 py-2 bg-fenlife-orange text-white text-sm font-semibold rounded-md hover:opacity-90 transition-opacity"
          >
            <FileUp size={15} />
            Rapor Üret
          </Link>
        </div>
      )}

      {!loading && students.length > 0 && (
        <>
          {/* Filtre araçları */}
          <div className="flex flex-wrap gap-3 mb-4">
            <div className="relative flex-1 min-w-[200px]">
              <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" />
              <input
                type="text"
                placeholder="Öğrenci ara…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 border border-stone-300 rounded-md text-sm bg-white text-stone-900 placeholder-stone-400 focus:outline-none focus:ring-1 focus:ring-fenlife-blue"
              />
            </div>
            <select
              value={gradeFilter}
              onChange={(e) => setGradeFilter(e.target.value)}
              className="px-3 py-2 border border-stone-300 rounded-md text-sm bg-white text-stone-800 focus:outline-none focus:ring-1 focus:ring-fenlife-blue"
            >
              <option value="all">Tüm Sınıflar</option>
              {gradeOptions.map((g) => (
                <option key={g} value={g}>{g}. Sınıf</option>
              ))}
            </select>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="px-3 py-2 border border-stone-300 rounded-md text-sm bg-white text-stone-800 focus:outline-none focus:ring-1 focus:ring-fenlife-blue"
            >
              {RISK_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>

          {filteredStudents.length === 0 ? (
            <div className="py-12 text-center border border-dashed border-stone-200 rounded-lg">
              <p className="text-stone-500 font-medium">Eşleşen öğrenci bulunamadı</p>
              <button
                onClick={() => { setSearchQuery(''); setGradeFilter('all'); setRiskFilter('all'); }}
                className="mt-3 text-sm text-fenlife-blue hover:underline"
              >
                Filtreleri temizle
              </button>
            </div>
          ) : (
            <div className="bg-white border border-stone-200 rounded-lg overflow-hidden">
              {hasActiveFilter && (
                <div className="px-4 py-2 bg-stone-50 border-b border-stone-200 text-xs text-stone-500">
                  {filteredStudents.length} / {students.length} öğrenci gösteriliyor
                </div>
              )}
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-stone-50 border-b border-stone-200 text-left">
                    <th className="px-4 py-3 font-semibold text-stone-700">Öğrenci</th>
                    <th className="px-4 py-3 font-semibold text-stone-700">Sınıf</th>
                    <th className="px-4 py-3 font-semibold text-stone-700 text-right">Ortalama</th>
                    <th className="px-4 py-3 font-semibold text-stone-700 text-right">Deneme</th>
                    <th className="px-4 py-3 font-semibold text-stone-700">Risk</th>
                    <th className="px-4 py-3 font-semibold text-stone-700">Trend</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStudents.map((s, i) => {
                    const risk = riskResult(s.risk_level);
                    return (
                      <tr
                        key={s.job_id}
                        onClick={() => router.push(`/dashboard?jobId=${s.job_id}`)}
                        className={`border-b border-stone-100 hover:bg-stone-50 transition-colors cursor-pointer ${
                          i % 2 === 1 ? 'bg-stone-50/40' : ''
                        }`}
                      >
                        <td className="px-4 py-3 font-medium text-stone-900">
                          {s.student_name || '—'}
                        </td>
                        <td className="px-4 py-3 text-stone-600">{s.student_grade || '—'}</td>
                        <td className="px-4 py-3 text-right font-mono font-semibold text-fenlife-blue">
                          {s.avg_puan != null ? s.avg_puan.toFixed(1) : '—'}
                        </td>
                        <td className="px-4 py-3 text-right text-stone-600">{s.exam_count ?? '—'}</td>
                        <td className="px-4 py-3">
                          {risk && <RiskBadge risk={risk} />}
                        </td>
                        <td className="px-4 py-3">
                          <TrendIcon direction={s.trend_direction} />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
