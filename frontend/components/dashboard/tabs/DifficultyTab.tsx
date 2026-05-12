'use client';

import { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer,
} from 'recharts';
import { Target } from 'lucide-react';
import { SUBJECT_META, DIFFICULTY_LEVELS } from '@/lib/types';
import type { MockStudent } from '@/lib/mock-data';

function hasRealData(d: MockStudent['difficulty']): boolean {
  return Object.values(d).some(
    (v) => Array.isArray(v.q) && v.q.length > 0 && v.q.some((n: number) => n > 0)
  );
}

function EmptyDifficultyState() {
  return (
    <div className="bg-white border border-stone-200 rounded-lg p-10 text-center">
      <div className="w-12 h-12 rounded-full bg-stone-100 flex items-center justify-center mx-auto mb-4">
        <Target size={22} className="text-stone-400" />
      </div>
      <p className="font-medium text-stone-700 mb-1">Zorluk profili verisi yok</p>
      <p className="text-sm text-stone-400 leading-relaxed max-w-sm mx-auto">
        Bu veri, sınav PDF&apos;lerinde soru bazlı zorluk bilgisi bulunduğunda otomatik oluşur.
        Mevcut parser yalnızca net sonuçları çıkarabilmektedir.
      </p>
    </div>
  );
}

export function DifficultyTab({ student }: { student: MockStudent }) {
  const [selectedSubject, setSelectedSubject] = useState<string>('matematik');

  if (!hasRealData(student.difficulty)) {
    return <EmptyDifficultyState />;
  }

  const d = student.difficulty[selectedSubject as keyof typeof student.difficulty];
  const subject = SUBJECT_META.find((s) => s.key === selectedSubject)!;

  const barData = DIFFICULTY_LEVELS.map((label, i) => {
    const totalQ = d?.q?.[i] ?? 0;
    const sSuccess = totalQ > 0 ? (( d?.sD?.[i] ?? 0) / totalQ) * 100 : 0;
    const gSuccess = totalQ > 0 ? ((d?.gD?.[i] ?? 0) / totalQ) * 100 : 0;
    return {
      zorluk: label,
      Öğrenci: Number(sSuccess.toFixed(0)),
      Kurum:   Number(gSuccess.toFixed(0)),
      soruSayisi: totalQ,
    };
  });

  const radarData = DIFFICULTY_LEVELS.map((label, i) => {
    const row: Record<string, string | number> = { zorluk: label };
    SUBJECT_META.forEach((s) => {
      const dd = student.difficulty[s.key as keyof typeof student.difficulty];
      const totalQ = dd?.q?.[i] ?? 0;
      row[s.label] = totalQ > 0 ? Number(((( dd?.sD?.[i] ?? 0) / totalQ) * 100).toFixed(0)) : 0;
    });
    return row;
  });

  return (
    <div className="space-y-5">
      <div className="bg-white border border-stone-200 rounded-lg p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-serif text-lg font-semibold text-stone-900">Zorluk Seviyesi Analizi</h3>
            <p className="text-xs text-stone-500">Her zorluk seviyesinde öğrenci ↔ kurum karşılaştırması</p>
          </div>
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="px-3 py-1.5 rounded-md border border-stone-300 text-sm bg-white text-stone-800"
          >
            {SUBJECT_META.map((s) => (
              <option key={s.key} value={s.key}>{s.label}</option>
            ))}
          </select>
        </div>
        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer>
            <BarChart data={barData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="zorluk" tick={{ fontSize: 11, fill: '#44403c' }} />
              <YAxis tick={{ fontSize: 10, fill: '#78716c' }} unit="%" />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e7e5e4' }}
                formatter={(v: number, n: string) => [`%${v}`, n]}
                labelFormatter={(label: string, payload) => {
                  if (!payload?.length) return label;
                  return `${label} (${(payload[0].payload as { soruSayisi: number }).soruSayisi} soru)`;
                }}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="Öğrenci" fill={subject.color} radius={[3, 3, 0, 0]} />
              <Bar dataKey="Kurum" fill="#A8A29E" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-3 text-xs text-stone-600 bg-stone-50 rounded-md p-3">
          <strong className="text-stone-900">Okuma ipucu:</strong> Kurum ortalaması altında kaldığı zorluk seviyeleri müdahale önceliği sunar. &ldquo;Kolay&rdquo; ve &ldquo;Çok Kolay&rdquo; seviyelerindeki açık, dikkat/işlem kaynaklı net kaybına işaret edebilir.
        </div>
      </div>

      <div className="bg-white border border-stone-200 rounded-lg p-5">
        <div className="mb-4">
          <h3 className="font-serif text-lg font-semibold text-stone-900">Tüm Dersler Zorluk Profili</h3>
          <p className="text-xs text-stone-500">Her zorluk seviyesinde öğrencinin ders bazlı başarı oranı</p>
        </div>
        <div style={{ width: '100%', height: 340 }}>
          <ResponsiveContainer>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#e7e5e4" />
              <PolarAngleAxis dataKey="zorluk" tick={{ fontSize: 11, fill: '#44403c' }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 9, fill: '#a8a29e' }} />
              {SUBJECT_META.map((s) => (
                <Radar
                  key={s.key}
                  name={s.label}
                  dataKey={s.label}
                  stroke={s.color}
                  fill={s.color}
                  fillOpacity={0.08}
                  strokeWidth={1.5}
                />
              ))}
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e7e5e4' }}
                formatter={(v: number) => [`%${v}`, '']}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
