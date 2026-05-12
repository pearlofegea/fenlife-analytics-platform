'use client';

import { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { computeSubjectAverages, formatDate } from '@/lib/analytics';
import { SUBJECT_META } from '@/lib/types';
import type { MockStudent } from '@/lib/mock-data';

export function TrendTab({ student }: { student: MockStudent }) {
  const [hidden, setHidden] = useState<Set<string>>(new Set());
  const subjectAvgs = computeSubjectAverages(student.exams);

  const chartData = student.exams.map((e) => {
    const row: Record<string, number | string> = { name: formatDate(e.date) };
    SUBJECT_META.forEach((s) => {
      row[s.key] = e[s.key as keyof typeof e] as number;
    });
    return row;
  });

  const toggle = (key: string) => {
    setHidden((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  return (
    <div className="space-y-5">
      <div className="bg-white border border-stone-200 rounded-lg p-5">
        <div className="mb-4">
          <h3 className="font-serif text-lg font-semibold text-stone-900">Ders Bazlı Sınav Trendi</h3>
          <p className="text-xs text-stone-500">Her dersin net hareketi — tıklayarak gizleyip gösterebilirsiniz</p>
        </div>
        <div className="flex flex-wrap gap-2 mb-3">
          {SUBJECT_META.map((s) => {
            const isHidden = hidden.has(s.key);
            return (
              <button
                key={s.key}
                onClick={() => toggle(s.key)}
                className={`px-2.5 py-1 rounded-full text-xs font-medium transition-opacity ${isHidden ? 'opacity-30' : ''}`}
                style={{ backgroundColor: s.color + '18', color: s.color, border: `1px solid ${s.color}40` }}
              >
                <span className="inline-block w-2 h-2 rounded-full mr-1.5" style={{ backgroundColor: s.color }} />
                {s.label}
              </button>
            );
          })}
        </div>
        <div style={{ width: '100%', height: 340 }}>
          <ResponsiveContainer>
            <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#78716c' }} />
              <YAxis tick={{ fontSize: 10, fill: '#78716c' }} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e7e5e4' }} />
              {SUBJECT_META.map(
                (s) =>
                  !hidden.has(s.key) && (
                    <Line
                      key={s.key}
                      type="monotone"
                      dataKey={s.key}
                      name={s.label}
                      stroke={s.color}
                      strokeWidth={2}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                    />
                  ),
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white border border-stone-200 rounded-lg overflow-hidden">
        <div className="p-5 border-b border-stone-200">
          <h3 className="font-serif text-lg font-semibold text-stone-900">Deneme Dökümü</h3>
          <p className="text-xs text-stone-500">Tüm denemeler — net ve puan bazında</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 text-xs uppercase tracking-wider text-stone-600">
              <tr>
                <th className="text-left py-2 px-3 font-medium">Tarih</th>
                <th className="text-left py-2 px-3 font-medium">Deneme</th>
                <th className="text-left py-2 px-3 font-medium">Yayın</th>
                {SUBJECT_META.map((s) => (
                  <th key={s.key} className="text-right py-2 px-3 font-medium">{s.label}</th>
                ))}
                <th className="text-right py-2 px-3 font-medium">Puan</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {student.exams.map((e, i) => (
                <tr key={i} className="hover:bg-stone-50">
                  <td className="py-2 px-3 text-stone-600 font-mono text-xs">{formatDate(e.date)}</td>
                  <td className="py-2 px-3 text-stone-900">{e.name}</td>
                  <td className="py-2 px-3 text-stone-600 text-xs">{e.publisher}</td>
                  {SUBJECT_META.map((s) => (
                    <td
                      key={s.key}
                      className="py-2 px-3 text-right font-mono text-stone-700"
                      style={{ fontVariantNumeric: 'tabular-nums' }}
                    >
                      {(e[s.key as keyof typeof e] as number).toFixed(2)}
                    </td>
                  ))}
                  <td
                    className="py-2 px-3 text-right font-semibold text-[#1B5E8C] font-mono"
                    style={{ fontVariantNumeric: 'tabular-nums' }}
                  >
                    {e.puan.toFixed(0)}
                  </td>
                </tr>
              ))}
              <tr className="bg-stone-100 font-semibold">
                <td className="py-2 px-3 text-stone-700" colSpan={3}>Ortalama</td>
                {subjectAvgs.map((s) => (
                  <td
                    key={s.key}
                    className="py-2 px-3 text-right font-mono"
                    style={{ color: s.color, fontVariantNumeric: 'tabular-nums' }}
                  >
                    {s.avg.toFixed(2)}
                  </td>
                ))}
                <td
                  className="py-2 px-3 text-right font-mono text-[#1B5E8C]"
                  style={{ fontVariantNumeric: 'tabular-nums' }}
                >
                  {student.avg_puan.toFixed(1)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
