'use client';

import { useMemo } from 'react';
import { GraduationCap, Target, BookOpen, ChevronRight, CheckCircle2 } from 'lucide-react';
import { computeRisk, computeTrend, computeSubjectAverages } from '@/lib/analytics';
import { DIFFICULTY_LEVELS, SUBJECT_META } from '@/lib/types';
import type { MockStudent } from '@/lib/mock-data';

function EmptyActionsState({ name }: { name: string }) {
  return (
    <div className="bg-white border border-stone-200 rounded-lg p-10 text-center">
      <div className="w-12 h-12 rounded-full bg-stone-100 flex items-center justify-center mx-auto mb-4">
        <CheckCircle2 size={22} className="text-stone-400" />
      </div>
      <p className="font-medium text-stone-700 mb-1">{name} için aksiyon verisi yok</p>
      <p className="text-sm text-stone-400 leading-relaxed max-w-sm mx-auto">
        Aksiyon paneli en az bir sınav verisi gerektirir. PDF yüklendiğinde ders bazlı
        öneriler, kazanım öncelikleri ve haftalık odak planı otomatik oluşacaktır.
      </p>
    </div>
  );
}

export function ActionsTab({ student }: { student: MockStudent }) {
  const subjectAvgs = computeSubjectAverages(student.exams);

  type GapResult = { subject: string; level: string; gap: string; studentPct: string; generalPct: string };

  const worstGap = useMemo((): GapResult | null => {
    let maxGap = 0;
    let result: GapResult | null = null;
    SUBJECT_META.forEach((s) => {
      const d = student.difficulty[s.key as keyof typeof student.difficulty];
      if (!d || !Array.isArray(d.q)) return; // veri yoksa atla
      [3, 4].forEach((i) => {
        const totalQ = d.q[i] ?? 0;
        if (totalQ === 0) return;
        const sPct = ((d.sD[i] ?? 0) / totalQ) * 100;
        const gPct = ((d.gD[i] ?? 0) / totalQ) * 100;
        const gap = gPct - sPct;
        if (gap > maxGap) {
          maxGap = gap;
          result = {
            subject: s.label,
            level: DIFFICULTY_LEVELS[i],
            gap: gap.toFixed(0),
            studentPct: sPct.toFixed(0),
            generalPct: gPct.toFixed(0),
          };
        }
      });
    });
    return result;
  }, [student]);

  // Sınav verisi yoksa aksiyon üretemeyiz
  if (student.exams.length === 0 || subjectAvgs.length === 0) {
    return <EmptyActionsState name={student.name} />;
  }

  const risk = computeRisk(student.avg_puan, student.exams);
  const trend = computeTrend(student.exams);
  const weakest = [...subjectAvgs].sort((a, b) => a.pct - b.pct)[0];
  const strongest = [...subjectAvgs].sort((a, b) => b.pct - a.pct)[0];
  const top3 = student.priorityTopics.slice(0, 3);

  const cards = [
    {
      Icon: GraduationCap,
      role: 'Branş Öğretmeni',
      color: '#1B5E8C',
      items: [
        {
          title: `${weakest.label} önceliği`,
          desc: `Ortalama ${weakest.avg.toFixed(1)} net (başarı %${weakest.pct.toFixed(0)}). En düşük performanslı ders — haftalık hedefli çalışma kağıtlarıyla konu tekrar planı kurulabilir.`,
        },
        ...top3.map((t) => ({
          title: `Kazanım: ${t.topic.slice(0, 60)}${t.topic.length > 60 ? '…' : ''}`,
          desc: `${t.subject} | ${t.q} soruda %${t.success} başarı, %${t.priority} öncelik. Bu kazanıma yönelik mini çalışma kağıdı + çözümlü anlatım önerilir.`,
        })),
      ],
    },
    {
      Icon: Target,
      role: 'Rehberlik',
      color: '#E87722',
      items: [
        risk.level === 'yuksek' && {
          title: 'Veli görüşmesi önerisi',
          desc: `Öğrenci ortalaması ${student.avg_puan.toFixed(0)} seviyesinde ve düşüş eğiliminde (${trend.delta.toFixed(0)} delta). Motivasyon ve sınav kaygısı üzerine aile desteği görüşmesi düzenlenebilir.`,
        },
        worstGap && Number(worstGap.gap) > 15 && {
          title: `${worstGap.subject}: ${worstGap.level} seviye kaybı`,
          desc: `Kurum ort. %${worstGap.generalPct}, öğrenci %${worstGap.studentPct} — ${worstGap.gap} puan fark. Dikkat/işlem kaynaklı net kaybı olasılığı; sınav stratejisi çalışması önerilir.`,
        },
        {
          title: `${strongest.label} güçlü yan olarak desteklenmeli`,
          desc: `Ortalama ${strongest.avg.toFixed(1)} net (başarı %${strongest.pct.toFixed(0)}). Öğrencinin özgüven inşasında bu ders kullanılabilir; zor soru pratiği artırılmalı.`,
        },
      ].filter(Boolean) as { title: string; desc: string }[],
    },
    {
      Icon: BookOpen,
      role: 'Çalışma Kağıdı Girdileri',
      color: '#2A8A8A',
      items: top3.length > 0
        ? top3.map((t) => ({
            title: `${t.subject} — ${t.topic.slice(0, 50)}${t.topic.length > 50 ? '…' : ''}`,
            desc: `${t.q} soruluk havuzda ${t.d} doğru, ${t.y} yanlış, ${t.b} boş. Kazanım eşleşmeli 5-8 soruluk mini çalışma kağıdı üretilebilir.`,
          }))
        : [{
            title: 'Kazanım verisi henüz yok',
            desc: 'Bu bölüm, soru-kazanım eşleşmesi içeren PDF formatlarında otomatik dolar. Mevcut parser yalnızca net sonuçları çıkarmaktadır.',
          }],
    },
  ];

  // Hiç içerik yoksa kartı gösterme
  const filledCards = cards.filter((c) => c.items.length > 0);

  return (
    <div className="space-y-5">
      <div className="bg-gradient-to-br from-[#1B5E8C] to-[#164A6E] text-white rounded-lg p-5">
        <div className="flex items-center gap-2 mb-2">
          <Target size={18} />
          <h3 className="font-serif text-lg font-semibold">Bu Haftanın Odak Planı</h3>
        </div>
        <p className="text-sm text-white/85 leading-relaxed">
          {student.name} için mevcut veriye göre aksiyon önerileri. Öncelik:{' '}
          <strong>maksimum net kaybı → tekrar eden hata → hızlı iyileşme potansiyeli</strong> mantığıyla sıralandı.
        </p>
        {student.exams.length < 5 && (
          <div className="mt-3 bg-white/10 border border-white/20 rounded-md p-3 text-xs leading-relaxed space-y-1">
            {student.exams.length === 1 ? (
              <>
                <p>
                  <strong>Tek sınav verisi:</strong> Kesin eğilim ve karşılaştırma yapılamaz.
                  Bu sınavda en düşük performans <strong>{weakest.label}</strong> dersinde
                  görülüyor (başarı %{weakest.pct.toFixed(0)}, ort. {weakest.avg.toFixed(1)} net) —
                  ders bazlı öneriler aşağıdadır.
                </p>
                <p>Güvenilir eğilim analizi ve gelişim takibi için en az 5 sınav yükleyin.</p>
              </>
            ) : (
              <p>
                <strong>{student.exams.length} sınav</strong> verisiyle temel karşılaştırma
                yapılabiliyor. Daha güvenilir eğilim analizi için en az 5 deneme önerilir.
                {weakest.pct < 50 && (
                  <> En kritik alan: <strong>{weakest.label}</strong> (%{weakest.pct.toFixed(0)}).</>
                )}
              </p>
            )}
          </div>
        )}
      </div>

      {filledCards.map((card, idx) => (
        <div key={idx} className="bg-white border border-stone-200 rounded-lg overflow-hidden">
          <div
            className="px-5 py-3 border-b border-stone-200 flex items-center gap-2"
            style={{ backgroundColor: card.color + '08' }}
          >
            <card.Icon size={18} style={{ color: card.color }} />
            <h4 className="font-serif text-base font-semibold" style={{ color: card.color }}>
              {card.role}
            </h4>
            <span className="ml-auto text-xs text-stone-500">{card.items.length} öneri</span>
          </div>
          <div className="divide-y divide-stone-100">
            {card.items.map((it, i) => (
              <div key={i} className="p-4 hover:bg-stone-50 transition-colors flex items-start gap-3">
                <ChevronRight size={14} className="mt-1 text-stone-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-stone-900 leading-snug">{it.title}</p>
                  <p className="text-xs text-stone-600 leading-relaxed mt-1">{it.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {subjectAvgs.length > 0 && (
        <div className="bg-stone-50 border border-stone-200 rounded-lg p-4 text-xs text-stone-600 leading-relaxed">
          <strong className="text-stone-800">Takip Hedefi:</strong> Bir sonraki denemede{' '}
          <strong>{weakest.label}</strong>&apos;de +2 net artış, toplam puanda +15 puan artış.
        </div>
      )}
    </div>
  );
}
