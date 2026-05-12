/**
 * FENlife veri modelleri — TypeScript.
 * Backend Pydantic modelleriyle senkron tutulmalı (app/models/, app/storage/).
 * Alan adı kuralı: backend ile aynı — snake_case API, camelCase yok.
 */

// ─── Temel modeller ───────────────────────────────────────────────────────────

export interface Exam {
  date: string;       // ISO: "2026-02-15"
  name: string;
  publisher: string;
  turkce: number;
  matematik: number;
  fen: number;
  sosyal: number;
  din: number;
  ydil: number;
  puan: number;
}

export interface Student {
  id: string | number;
  name: string;
  grade: string;      // "8-01"  (eski: class — reserved keyword, grade kullanılır)
  avg_puan: number;
  exams: Exam[];
}

// ─── Risk & Trend ─────────────────────────────────────────────────────────────

export type RiskLevel = 'dusuk' | 'orta' | 'yuksek' | 'sinirli';

export interface RiskResult {
  level: RiskLevel;
  label: string;
  color: string;
}

export interface TrendResult {
  slope: number;
  delta: number;
  direction: 'up' | 'down' | 'flat';
}

// ─── Konu / Kazanım ───────────────────────────────────────────────────────────

export interface PriorityTopic {
  rank: number;
  subject: string;
  topic: string;
  q: number;      // toplam soru
  d: number;      // doğru
  y: number;      // yanlış
  b: number;      // boş
  success: number; // başarı %
  priority: number; // öncelik skoru
}

// ─── Zorluk profili ───────────────────────────────────────────────────────────

export interface DifficultyProfile {
  q: number[];    // soru sayısı   [ÇokZor, Zor, Orta, Kolay, ÇokKolay]
  sD: number[];   // öğrenci doğru
  sY: number[];   // öğrenci yanlış
  gD: number[];   // genel doğru
  gY: number[];   // genel yanlış
}

export interface SubjectDifficulty {
  turkce: DifficultyProfile;
  matematik: DifficultyProfile;
  fen: DifficultyProfile;
  sosyal: DifficultyProfile;
  din: DifficultyProfile;
  ydil: DifficultyProfile;
}

// ─── Ders ortalamaları ────────────────────────────────────────────────────────

export interface SubjectAverage {
  key: string;
  label: string;
  qCount: number;
  color: string;
  avg: number;
  max: number;
  min: number;
  last: number;
  pct: number;    // avg / qCount * 100
}

// ─── Dashboard veri sözleşmesi ────────────────────────────────────────────────

export interface DashboardData {
  student: Student;
  exams: Exam[];
  subject_averages: SubjectAverage[];
  trend: TrendResult;
  risk: RiskResult;
  difficulty: SubjectDifficulty;
  priority_topics: PriorityTopic[];
}

// ─── API response tipleri ─────────────────────────────────────────────────────

export interface CreateReportResponse {
  job_id: string;
  status: string;
  file_count: number;
  data_warning?: string | null;
  message?: string;
}

export interface ReportStatusResponse {
  job_id: string;
  status: 'processing' | 'completed' | 'failed';
  student_name?: string;
  student_grade?: string;
  exam_count?: number;
  publishers?: string[];
  avg_puan?: number;
  risk_level?: RiskLevel;
  trend_direction?: 'up' | 'down' | 'flat';
  created_at: string;
  download_url?: string;
  error?: string;
}

// ─── Sabitler ─────────────────────────────────────────────────────────────────

export const SUBJECT_META = [
  { key: 'turkce',    label: 'Türkçe',       qCount: 20, color: '#1B5E8C' },
  { key: 'matematik', label: 'Matematik',    qCount: 20, color: '#E87722' },
  { key: 'fen',       label: 'Fen Bilimleri', qCount: 20, color: '#2A8A8A' },
  { key: 'sosyal',    label: 'İnkılap',      qCount: 10, color: '#8B5A3C' },
  { key: 'din',       label: 'Din Kültürü',  qCount: 10, color: '#6B4E9B' },
  { key: 'ydil',      label: 'Y. Dil',       qCount: 10, color: '#9B4E6B' },
] as const;

export const DIFFICULTY_LEVELS = ['Çok Zor', 'Zor', 'Orta', 'Kolay', 'Çok Kolay'] as const;
