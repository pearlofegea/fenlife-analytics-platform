'use client';

import { useState } from 'react';
import { BookOpen } from 'lucide-react';
import type { MockStudent } from '@/lib/mock-data';

const SUBJECT_COLORS: Record<string, string> = {
  Türkçe:    '#1B5E8C',
  Matematik:  '#E87722',
  Fen:        '#2A8A8A',
  Sosyal:     '#8B5A3C',
  Din:        '#6B4E9B',
};

function EmptyTopicsState() {
  return (
    <div className="bg-white border border-stone-200 rounded-lg p-10 text-center">
      <div className="w-12 h-12 rounded-full bg-stone-100 flex items-center justify-center mx-auto mb-4">
        <BookOpen size={22} className="text-stone-400" />
      </div>
      <p className="font-medium text-stone-700 mb-1">Kazanım verisi henüz yok</p>
      <p className="text-sm text-stone-400 leading-relaxed max-w-sm mx-auto">
        Bu bölüm, soru-kazanım eşleşmesi içeren PDF formatlarında otomatik dolar.
        Mevcut parser yalnızca net sonuçları (doğru/yanlış/boş) çıkarabilmektedir;
        konu bazlı öncelik analizi henüz desteklenmemektedir.
      </p>
    </div>
  );
}

export function TopicsTab({ student }: { student: MockStudent }) {
  const [filter, setFilter] = useState<string>('all');

  if (student.priorityTopics.length === 0) {
    return <EmptyTopicsState />;
  }

  const filtered =
    filter === 'all'
      ? student.priorityTopics
      : student.priorityTopics.filter((t) => t.subject === filter);

  const subjectCounts = student.priorityTopics.reduce<Record<string, number>>((acc, t) => {
    acc[t.subject] = (acc[t.subject] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-5">
      <div className="bg-white border border-stone-200 rounded-lg p-5">
        <div className="mb-4">
          <h3 className="font-serif text-lg font-semibold text-stone-900">Öncelikli Gelişim Alanları</h3>
          <p className="text-xs text-stone-500">Kazanım bazlı çalışma öncelikleri — yüzdelik öncelik puanına göre</p>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              filter === 'all' ? 'bg-stone-900 text-white' : 'bg-stone-100 text-stone-700 hover:bg-stone-200'
            }`}
          >
            Tümü ({student.priorityTopics.length})
          </button>
          {Object.entries(subjectCounts).map(([subj, count]) => (
            <button
              key={subj}
              onClick={() => setFilter(subj)}
              className="px-3 py-1.5 rounded-full text-xs font-medium transition-all"
              style={
                filter === subj
                  ? { backgroundColor: SUBJECT_COLORS[subj] || '#1B5E8C', color: '#fff' }
                  : { backgroundColor: '#f5f5f4', color: '#44403c' }
              }
            >
              {subj} ({count})
            </button>
          ))}
        </div>

        <div className="space-y-2">
          {filtered.map((t, idx) => {
            const color = SUBJECT_COLORS[t.subject] || '#1B5E8C';
            return (
              <div
                key={idx}
                className="flex items-start gap-3 p-3 border border-stone-200 rounded-lg hover:border-stone-300 transition-colors"
              >
                <div
                  className="flex-shrink-0 w-10 h-10 rounded-md flex items-center justify-center font-serif font-semibold text-sm"
                  style={{ backgroundColor: color + '15', color }}
                >
                  #{t.rank}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded"
                      style={{ backgroundColor: color + '15', color }}
                    >
                      {t.subject}
                    </span>
                    <span className="text-[10px] text-stone-500 font-mono">
                      {t.q} soru · {t.d}D / {t.y}Y / {t.b}B
                    </span>
                  </div>
                  <p className="text-sm text-stone-900 leading-snug">{t.topic}</p>
                  <div className="mt-2 flex items-center gap-3">
                    <div className="flex-1 h-1.5 bg-stone-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full"
                        style={{ width: t.priority + '%', backgroundColor: color }}
                      />
                    </div>
                    <span className="text-xs font-mono text-stone-600 tabular-nums" style={{ minWidth: 48 }}>
                      %{t.priority} öncelik
                    </span>
                    <span className="text-xs font-mono text-stone-500 tabular-nums" style={{ minWidth: 60 }}>
                      Başarı %{t.success}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
