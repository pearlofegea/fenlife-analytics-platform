'use client';

import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Activity, TrendingUp, Target, BookOpen, CheckCircle2, Loader2, FileUp, Users } from 'lucide-react';
import { computeRisk } from '@/lib/analytics';
import { RiskBadge } from './shared/RiskBadge';
import { StudentSelector } from './StudentSelector';
import { OverviewTab } from './tabs/OverviewTab';
import { TrendTab } from './tabs/TrendTab';
import { DifficultyTab } from './tabs/DifficultyTab';
import { TopicsTab } from './tabs/TopicsTab';
import { ActionsTab } from './tabs/ActionsTab';
import { apiClient } from '@/lib/api-client';
import type { MockStudent } from '@/lib/mock-data';
import type { SubjectDifficulty, PriorityTopic } from '@/lib/types';

// ─── Tipler ────────────────────────────────────────────────────────────────────

export interface StudentSummary {
  job_id: string;
  name: string;
  grade: string;
  avg_puan: number;
  exam_count: number;
  risk_level: string;
  trend_direction: 'up' | 'down' | 'flat';
  created_at: string | null;
}

interface StudentDetailData {
  name: string;
  grade: string;
  avg_puan: number;
  exams: MockStudent['exams'];
  priority_topics: PriorityTopic[];
  difficulty: Record<string, unknown>;
  risk: { level: string; label: string };
  trend: { slope: number; delta: number; direction: 'up' | 'down' | 'flat' };
}

// ─── Yardımcılar ──────────────────────────────────────────────────────────────

const EMPTY_DIFFICULTY: SubjectDifficulty = {
  turkce:    { q: [], sD: [], sY: [], gD: [], gY: [] },
  matematik: { q: [], sD: [], sY: [], gD: [], gY: [] },
  fen:       { q: [], sD: [], sY: [], gD: [], gY: [] },
  sosyal:    { q: [], sD: [], sY: [], gD: [], gY: [] },
  din:       { q: [], sD: [], sY: [], gD: [], gY: [] },
  ydil:      { q: [], sD: [], sY: [], gD: [], gY: [] },
};

function hasRealDifficulty(raw: Record<string, unknown>): boolean {
  // {} truthy olduğu için || ile guard yapılamaz — key sayısını + veri varlığını kontrol et
  if (!raw || typeof raw !== 'object') return false;
  return Object.values(raw).some((v) => {
    const d = v as { q?: number[] };
    return Array.isArray(d?.q) && d.q.length > 0 && d.q.some((n) => n > 0);
  });
}

function adaptDetailToStudent(jobId: string, data: StudentDetailData): MockStudent {
  return {
    id: parseInt(jobId.slice(-6), 16) % 100000,
    name: data.name,
    grade: data.grade,
    avg_puan: data.avg_puan,
    exams: data.exams || [],
    difficulty: hasRealDifficulty(data.difficulty)
      ? (data.difficulty as unknown as SubjectDifficulty)
      : EMPTY_DIFFICULTY,
    priorityTopics: (data.priority_topics || []) as PriorityTopic[],
  };
}

/**
 * Aynı isim+sınıf kombinasyonundan sadece en güncel job'ı tut.
 * Aynı öğrencinin birden fazla raporu varsa yalnızca en son yükleme gösterilir.
 */
function deduplicateStudents(students: StudentSummary[]): StudentSummary[] {
  const map = new Map<string, StudentSummary>();
  for (const s of students) {
    const key = `${s.name.trim().toLowerCase()}|${s.grade.trim().toLowerCase()}`;
    const existing = map.get(key);
    if (!existing) {
      map.set(key, s);
    } else {
      // created_at varsa daha güncel olanı tut, yoksa exam_count'u tercih et
      const currentDate = s.created_at ?? '';
      const existingDate = existing.created_at ?? '';
      if (currentDate > existingDate) map.set(key, s);
    }
  }
  return Array.from(map.values());
}

// ─── Tab config ───────────────────────────────────────────────────────────────

type TabKey = 'overview' | 'trend' | 'difficulty' | 'topics' | 'actions';

const TABS: { key: TabKey; label: string; Icon: React.ElementType }[] = [
  { key: 'overview',   label: 'Genel Bakış',      Icon: Activity     },
  { key: 'trend',      label: 'Sınav Trendi',     Icon: TrendingUp   },
  { key: 'difficulty', label: 'Zorluk Profili',   Icon: Target       },
  { key: 'topics',     label: 'Gelişim Alanları', Icon: BookOpen     },
  { key: 'actions',    label: 'Aksiyon Paneli',   Icon: CheckCircle2 },
];

// ─── Boş durum bileşeni ───────────────────────────────────────────────────────

function EmptyState() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center max-w-sm mx-auto">
        <div className="w-16 h-16 rounded-full bg-fenlife-orange-soft flex items-center justify-center mx-auto mb-5">
          <Users size={28} className="text-fenlife-orange" />
        </div>
        <h2 className="font-serif text-xl font-semibold text-stone-900 mb-2">
          Henüz analiz edilmiş öğrenci yok
        </h2>
        <p className="text-sm text-stone-500 mb-6 leading-relaxed">
          Sınav PDF dosyalarını yükleyin — sistem otomatik olarak analiz eder ve öğrenci dashboardunu doldurur.
        </p>
        <Link
          href="/reports/generate"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-fenlife-blue text-white text-sm font-semibold rounded-md hover:bg-fenlife-blue-dark transition-colors"
        >
          <FileUp size={16} />
          İlk Raporu Oluştur
        </Link>
      </div>
    </div>
  );
}

// ─── Ana bileşen ──────────────────────────────────────────────────────────────

export function DashboardShell() {
  const searchParams = useSearchParams();
  const jobIdParam = searchParams.get('jobId');

  const [summaries, setSummaries] = useState<StudentSummary[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [activeStudent, setActiveStudent] = useState<MockStudent | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [fetchError, setFetchError] = useState(false);

  // İlk yükleme: öğrenci listesini API'den çek
  useEffect(() => {
    async function fetchList() {
      try {
        const res = await apiClient.listStudents() as { students: Array<{
          job_id: string; student_name: string; student_grade: string;
          avg_puan: number; risk_level: string; trend_direction: string;
          exam_count: number; created_at: string | null;
        }> };

        const raw: StudentSummary[] = res.students
          .filter((s) => s.student_name && s.student_name.trim() !== '' && (s.exam_count ?? 0) > 0)
          .map((s) => ({
            job_id:          s.job_id,
            name:            s.student_name ?? '—',
            grade:           s.student_grade ?? '—',
            avg_puan:        s.avg_puan ?? 0,
            exam_count:      s.exam_count ?? 0,
            risk_level:      s.risk_level ?? 'sinirli',
            trend_direction: (s.trend_direction ?? 'flat') as 'up' | 'down' | 'flat',
            created_at:      s.created_at ?? null,
          }));

        const unique = deduplicateStudents(raw);
        setSummaries(unique);
        if (unique.length > 0) {
          const paramMatch = jobIdParam ? unique.find((s) => s.job_id === jobIdParam) : null;
          setSelectedJobId(paramMatch ? paramMatch.job_id : unique[0].job_id);
        }
      } catch {
        setFetchError(true);
      } finally {
        setLoadingList(false);
      }
    }
    fetchList();
  }, [jobIdParam]);

  // Öğrenci seçilince detayı yükle
  const loadDetail = useCallback(async (jobId: string) => {
    setLoadingDetail(true);
    try {
      const data = await apiClient.getDashboard(jobId) as unknown as StudentDetailData;
      setActiveStudent(adaptDetailToStudent(jobId, data));
    } catch {
      // dashboard_data yoksa (eski job) özet bilgiden minimal görünüm oluştur
      const summary = summaries.find((s) => s.job_id === jobId);
      if (summary) {
        setActiveStudent({
          id: parseInt(jobId.slice(-6), 16) % 100000,
          name: summary.name,
          grade: summary.grade,
          avg_puan: summary.avg_puan,
          exams: [],
          difficulty: EMPTY_DIFFICULTY,
          priorityTopics: [],
        });
      }
    } finally {
      setLoadingDetail(false);
    }
  }, [summaries]);

  useEffect(() => {
    if (selectedJobId) loadDetail(selectedJobId);
  }, [selectedJobId, loadDetail]);

  const totalExams = summaries.reduce((sum, s) => sum + s.exam_count, 0);
  const risk = activeStudent ? computeRisk(activeStudent.avg_puan, activeStudent.exams) : null;

  // ─── Yükleniyor ──────────────────────────────────────────────────────────────
  if (loadingList) {
    return (
      <div className="min-h-screen bg-fenlife-cream flex items-center justify-center">
        <div className="flex items-center gap-2 text-stone-500">
          <Loader2 size={20} className="animate-spin" />
          <span className="text-sm">Yükleniyor…</span>
        </div>
      </div>
    );
  }

  // ─── Hata ────────────────────────────────────────────────────────────────────
  if (fetchError) {
    return (
      <div className="min-h-screen bg-fenlife-cream flex items-center justify-center">
        <div className="text-center max-w-sm">
          <p className="text-stone-600 font-medium mb-2">Backend&apos;e bağlanılamadı</p>
          <p className="text-sm text-stone-400">FastAPI çalışıyor mu? Port 8000 erişilebilir mi?</p>
        </div>
      </div>
    );
  }

  // ─── Boş durum ───────────────────────────────────────────────────────────────
  if (summaries.length === 0) {
    return (
      <div className="min-h-screen bg-fenlife-cream">
        <div className="max-w-7xl mx-auto px-5 py-6">
          <EmptyState />
        </div>
      </div>
    );
  }

  // ─── Ana görünüm ──────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-fenlife-cream">
      <div className="max-w-7xl mx-auto px-5 py-6">
        <StudentSelector
          students={summaries}
          selectedJobId={selectedJobId}
          onSelect={(jobId) => {
            setSelectedJobId(jobId);
            setActiveTab('overview');
          }}
          totalExams={totalExams}
        />

        {loadingDetail ? (
          <div className="bg-white border border-stone-200 rounded-lg p-8 flex items-center justify-center gap-2 text-stone-400 mb-5">
            <Loader2 size={18} className="animate-spin" />
            <span className="text-sm">Öğrenci verisi yükleniyor…</span>
          </div>
        ) : activeStudent ? (
          <>
            <div className="bg-white border border-stone-200 rounded-lg p-5 mb-5">
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] uppercase tracking-widest text-stone-500 font-semibold">
                      {selectedJobId?.slice(0, 8)}…
                    </span>
                    {risk && <RiskBadge risk={risk} />}
                  </div>
                  <h3 className="font-serif text-3xl font-semibold text-stone-900">{activeStudent.name}</h3>
                  <p className="text-sm text-stone-600 mt-1">
                    {activeStudent.grade} sınıfı ·{' '}
                    {activeStudent.exams.length > 0
                      ? `${activeStudent.exams.length} deneme · Ortalama `
                      : 'Ortalama '}
                    <span className="font-mono font-semibold text-fenlife-blue">
                      {activeStudent.avg_puan.toFixed(1)}
                    </span>{' '}
                    puan
                  </p>
                </div>
                <div className="flex items-center gap-1 flex-wrap">
                  {TABS.map(({ key, label, Icon }) => (
                    <button
                      key={key}
                      onClick={() => setActiveTab(key)}
                      disabled={activeStudent.exams.length === 0 && key !== 'overview'}
                      className={`px-3 py-2 rounded-md text-xs font-semibold flex items-center gap-1.5 transition-all disabled:opacity-40 disabled:cursor-not-allowed ${
                        activeTab === key
                          ? 'bg-fenlife-blue text-white shadow-sm'
                          : 'text-stone-600 hover:bg-stone-100'
                      }`}
                    >
                      <Icon size={13} />
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {activeStudent.exams.length === 0 ? (
              <div className="bg-white border border-stone-200 rounded-lg p-10 text-center">
                <p className="text-stone-500 font-medium mb-1">Sınav detayları henüz işlenmemiş</p>
                <p className="text-sm text-stone-400">
                  Bu öğrencinin raporunu tekrar yüklerseniz tam analiz görünecek.
                </p>
              </div>
            ) : (
              <>
                {activeTab === 'overview'   && <OverviewTab   student={activeStudent} />}
                {activeTab === 'trend'      && <TrendTab      student={activeStudent} />}
                {activeTab === 'difficulty' && <DifficultyTab student={activeStudent} />}
                {activeTab === 'topics'     && <TopicsTab     student={activeStudent} />}
                {activeTab === 'actions'    && <ActionsTab    student={activeStudent} />}
              </>
            )}
          </>
        ) : null}

        <footer className="mt-8 pt-5 border-t border-stone-200 text-xs text-stone-500 flex items-center justify-between">
          <div>
            <span className="font-serif text-fenlife-blue font-semibold">FENlife Analytics</span>{' '}
            · Sınav sonuçları analiz platformu
          </div>
          <div className="text-stone-400">Akademik Gelişim ve Takip Planlama</div>
        </footer>
      </div>
    </div>
  );
}
