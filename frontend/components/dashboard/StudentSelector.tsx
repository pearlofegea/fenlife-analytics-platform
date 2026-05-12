'use client';

import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { RiskBadge } from './shared/RiskBadge';
import type { StudentSummary } from './DashboardShell';
import type { RiskLevel } from '@/lib/types';

function riskFromLevel(level: string) {
  const map: Record<string, { level: RiskLevel; label: string; color: string }> = {
    dusuk:   { level: 'dusuk',   label: 'Düşük Risk',  color: '#15803D' },
    orta:    { level: 'orta',    label: 'Orta Risk',   color: '#D97706' },
    yuksek:  { level: 'yuksek',  label: 'Yüksek Risk', color: '#DC2626' },
    sinirli: { level: 'sinirli', label: 'Sınırlı',     color: '#6B7280' },
  };
  return map[level] ?? map['sinirli'];
}

interface StudentCardProps {
  student: StudentSummary;
  isSelected: boolean;
  onClick: () => void;
}

function StudentCard({ student, isSelected, onClick }: StudentCardProps) {
  const risk = riskFromLevel(student.risk_level);
  const direction = student.trend_direction;
  const TrendIcon =
    direction === 'up' ? TrendingUp : direction === 'down' ? TrendingDown : Minus;
  const trendColor =
    direction === 'up' ? '#15803D' : direction === 'down' ? '#B91C1C' : '#737373';

  return (
    <button
      onClick={onClick}
      className={`text-left p-4 rounded-lg border transition-all ${
        isSelected
          ? 'border-[#1B5E8C] bg-[#1B5E8C]/5 shadow-sm'
          : 'border-stone-200 bg-white hover:border-stone-300 hover:shadow-sm'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <p className="text-xs text-stone-500 font-mono">{student.grade}</p>
          <p className="font-semibold text-stone-900 text-sm leading-tight">{student.name}</p>
        </div>
        <TrendIcon size={16} style={{ color: trendColor }} />
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-xs text-stone-500">Ortalama</p>
          <p
            className="text-lg font-serif font-semibold text-stone-900"
            style={{ fontVariantNumeric: 'tabular-nums' }}
          >
            {student.avg_puan.toFixed(0)}
          </p>
        </div>
        <RiskBadge risk={risk} />
      </div>
      <p className="text-[10px] text-stone-400 mt-1">{student.exam_count} deneme</p>
    </button>
  );
}

interface StudentSelectorProps {
  students: StudentSummary[];
  selectedJobId: string | null;
  onSelect: (jobId: string) => void;
  totalExams: number;
}

export function StudentSelector({ students, selectedJobId, onSelect, totalExams }: StudentSelectorProps) {
  return (
    <div className="mb-5">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="font-serif text-2xl font-semibold text-stone-900">Öğrenci Analizi</h2>
          <p className="text-sm text-stone-600 mt-0.5">
            Bir öğrenci seçerek detaylı sınav analizini görüntüleyin
          </p>
        </div>
        <div className="text-xs text-stone-500">
          <span className="font-mono text-stone-700">{students.length}</span> öğrenci ·{' '}
          <span className="font-mono text-stone-700">{totalExams}</span> deneme analiz edildi
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {students.map((s) => (
          <StudentCard
            key={s.job_id}
            student={s}
            isSelected={s.job_id === selectedJobId}
            onClick={() => onSelect(s.job_id)}
          />
        ))}
      </div>
    </div>
  );
}
