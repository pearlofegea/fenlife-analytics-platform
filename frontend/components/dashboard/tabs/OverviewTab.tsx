'use client';

import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, Cell, ResponsiveContainer,
} from 'recharts';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Award, Activity, AlertCircle } from 'lucide-react';
import { computeTrend, computeRisk, computeSubjectAverages, formatDate } from '@/lib/analytics';
import { StatCard } from '../shared/StatCard';
import type { MockStudent } from '@/lib/mock-data';

export function OverviewTab({ student }: { student: MockStudent }) {
  if (student.exams.length === 0) {
    return (
      <div className="bg-white border border-stone-200 rounded-lg p-10 text-center">
        <p className="font-medium text-stone-700 mb-1">Sınav verisi bulunamadı</p>
        <p className="text-sm text-stone-400">Detaylı analiz için PDF yükleyin.</p>
      </div>
    );
  }

  const risk = computeRisk(student.avg_puan, student.exams);
  const trend = computeTrend(student.exams);
  const subjectAvgs = computeSubjectAverages(student.exams);
  const lastExam = student.exams[student.exams.length - 1];
  const puanlar = student.exams.map((e) => e.puan);
  const maxPuan = Math.max(...puanlar);
  const minPuan = Math.min(...puanlar);
  const volatility = maxPuan - minPuan;

  const chartData = student.exams.map((e) => ({
    name: formatDate(e.date),
    puan: Math.round(e.puan),
  }));

  const subjectPctData = subjectAvgs.map((s) => ({
    ders: s.label,
    yuzde: Number(s.pct.toFixed(1)),
    ortNet: Number(s.avg.toFixed(2)),
    fill: s.color,
  }));

  const TrendIcon =
    trend.direction === 'up' ? TrendingUp : trend.direction === 'down' ? TrendingDown : Minus;
  const trendColor =
    trend.direction === 'up' ? '#15803D' : trend.direction === 'down' ? '#B91C1C' : '#737373';

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <StatCard
          icon={Award}
          label="Ortalama Puan"
          value={student.avg_puan.toFixed(1)}
          sublabel={`${student.exams.length} deneme`}
          accent="#1B5E8C"
        />
        <StatCard
          icon={Activity}
          label="Son Deneme"
          value={lastExam.puan.toFixed(0)}
          sublabel={formatDate(lastExam.date)}
          accent={lastExam.puan > student.avg_puan ? '#15803D' : '#B91C1C'}
          iconColor={lastExam.puan > student.avg_puan ? '#15803D' : '#B91C1C'}
        />
        <StatCard
          icon={TrendIcon}
          label="Trend (ilk → son)"
          value={(trend.delta >= 0 ? '+' : '') + trend.delta.toFixed(0)}
          sublabel={trend.direction === 'up' ? 'Yükseliş' : trend.direction === 'down' ? 'Düşüş' : 'Stabil'}
          accent={trendColor}
          iconColor={trendColor}
        />
        <StatCard
          icon={AlertCircle}
          label="Tutarlılık"
          value={volatility.toFixed(0) + ' puan'}
          sublabel="Min-Maks aralığı"
          accent={volatility > 100 ? '#E87722' : '#15803D'}
          iconColor={volatility > 100 ? '#E87722' : '#15803D'}
        />
      </div>

      <div
        className="rounded-lg p-4 flex items-start gap-3 border"
        style={{ borderColor: risk.color + '40', backgroundColor: risk.color + '0a' }}
      >
        <AlertTriangle size={20} style={{ color: risk.color, flexShrink: 0, marginTop: 2 }} />
        <div>
          <p className="text-sm font-semibold" style={{ color: risk.color }}>
            Genel Değerlendirme: {risk.label}
          </p>
          <p className="text-xs text-stone-700 mt-1 leading-relaxed">
            {risk.level === 'yuksek' &&
              `Ortalama ${student.avg_puan.toFixed(0)} puan, son denemelerde düşüş gözlemleniyor (${trend.delta > 0 ? '+' : ''}${trend.delta.toFixed(0)} delta). Yakın takip ve hedefli müdahale önerilir.`}
            {risk.level === 'orta' &&
              `Ortalama ${student.avg_puan.toFixed(0)} puan, dalgalı bir performans profili (${volatility.toFixed(0)} puan aralık) mevcut. İstikrarı artıracak çalışma planı önerilir.`}
            {risk.level === 'dusuk' &&
              `Ortalama ${student.avg_puan.toFixed(0)} puan, pozitif trend mevcut. Mevcut tempo sürdürülerek hedef puan üstüne zorlanabilir.`}
            {risk.level === 'sinirli' &&
              `${student.exams.length} deneme verisiyle temel bir görüntü sunuluyor. Daha güvenilir analiz ve eğilim yorumları için en az 5 sınav verisi önerilir.`}
          </p>
        </div>
      </div>

      <div className="bg-white border border-stone-200 rounded-lg p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-serif text-lg font-semibold text-stone-900">Puan Gelişim Grafiği</h3>
            <p className="text-xs text-stone-500">Tüm denemelerin puan hareketi</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-stone-500">Aralık</p>
            <p className="text-sm font-mono text-stone-700">
              {minPuan.toFixed(0)} — {maxPuan.toFixed(0)}
            </p>
          </div>
        </div>
        <div style={{ width: '100%', height: 260 }}>
          <ResponsiveContainer>
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="gradPuan" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#1B5E8C" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#1B5E8C" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#78716c' }} />
              <YAxis domain={['dataMin - 20', 'dataMax + 20']} tick={{ fontSize: 10, fill: '#78716c' }} />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e7e5e4' }}
                formatter={(v) => [v + ' puan', 'Puan']}
              />
              <ReferenceLine
                y={student.avg_puan}
                stroke="#E87722"
                strokeDasharray="4 4"
                label={{ value: `Ort. ${student.avg_puan.toFixed(0)}`, position: 'insideTopRight', fill: '#E87722', fontSize: 10 }}
              />
              <Area type="monotone" dataKey="puan" stroke="#1B5E8C" strokeWidth={2} fill="url(#gradPuan)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white border border-stone-200 rounded-lg p-5">
        <div className="mb-4">
          <h3 className="font-serif text-lg font-semibold text-stone-900">Ders Bazlı Başarı Oranı</h3>
          <p className="text-xs text-stone-500">Soru sayısına göre yüzdelik ortalama</p>
        </div>
        <div style={{ width: '100%', height: 260 }}>
          <ResponsiveContainer>
            <BarChart data={subjectPctData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="ders" tick={{ fontSize: 11, fill: '#44403c' }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#78716c' }} unit="%" />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e7e5e4' }}
                formatter={(v: number, _n: string, p) => [`%${v} (${p.payload.ortNet} net)`, 'Başarı']}
              />
              <Bar dataKey="yuzde" radius={[4, 4, 0, 0]}>
                {subjectPctData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mt-4 pt-4 border-t border-stone-100">
          {subjectAvgs.map((s) => (
            <div key={s.key} className="text-center">
              <div className="w-2 h-2 rounded-full mx-auto mb-1" style={{ backgroundColor: s.color }} />
              <p className="text-xs text-stone-500">{s.label}</p>
              <p
                className="text-sm font-semibold text-stone-900"
                style={{ fontVariantNumeric: 'tabular-nums' }}
              >
                {s.avg.toFixed(2)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
