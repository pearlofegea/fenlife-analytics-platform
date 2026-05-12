'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { FileText, Download, Plus, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import type { RiskLevel } from '@/lib/types';

interface ReportRow {
  job_id: string;
  student_name: string | null;
  student_grade: string | null;
  exam_count: number | null;
  avg_puan: number | null;
  risk_level: RiskLevel | null;
  created_at: string | null;
}

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.listStudents()
      .then((res) => setReports((res as { students: ReportRow[] }).students))
      .catch(() => setReports([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <FileText size={22} className="text-fenlife-blue" />
            <h1 className="font-serif text-2xl font-bold text-stone-900">Raporlar</h1>
          </div>
          <p className="text-sm text-stone-500">Üretilmiş tüm raporlar ve indirme bağlantıları</p>
        </div>
        <Link
          href="/reports/generate"
          className="inline-flex items-center gap-2 px-4 py-2 bg-fenlife-blue text-white text-sm font-semibold rounded-md hover:bg-fenlife-blue-dark transition-colors"
        >
          <Plus size={16} />
          Yeni Rapor
        </Link>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16 gap-2 text-stone-500">
          <Loader2 size={18} className="animate-spin" />
          <span className="text-sm">Yükleniyor…</span>
        </div>
      )}

      {!loading && reports.length === 0 && (
        <div className="py-16 text-center border border-dashed border-stone-300 rounded-lg">
          <FileText size={40} className="mx-auto text-stone-300 mb-3" />
          <p className="text-stone-500 font-medium">Henüz rapor oluşturulmadı</p>
          <p className="text-sm text-stone-400 mt-1 mb-4">
            Sınav PDF&apos;lerini yükleyerek ilk raporunuzu oluşturun.
          </p>
          <Link
            href="/reports/generate"
            className="inline-flex items-center gap-2 px-4 py-2 bg-fenlife-orange text-white text-sm font-semibold rounded-md hover:opacity-90 transition-opacity"
          >
            <Plus size={16} />
            Rapor Üret
          </Link>
        </div>
      )}

      {!loading && reports.length > 0 && (
        <div className="space-y-3">
          {reports.map((r) => (
            <div
              key={r.job_id}
              className="bg-white border border-stone-200 rounded-lg p-4 flex items-center justify-between gap-4"
            >
              <div className="flex items-center gap-3">
                <CheckCircle2 size={20} className="text-green-600 flex-shrink-0" />
                <div>
                  <p className="font-semibold text-stone-900 text-sm">
                    {r.student_name ?? 'Bilinmeyen Öğrenci'}
                  </p>
                  <p className="text-xs text-stone-500 mt-0.5">
                    {r.student_grade && <span className="mr-2">{r.student_grade}</span>}
                    {r.exam_count != null && <span className="mr-2">{r.exam_count} deneme</span>}
                    {r.avg_puan != null && (
                      <span className="font-mono text-fenlife-blue font-semibold">
                        ort. {r.avg_puan.toFixed(0)}
                      </span>
                    )}
                  </p>
                  {r.created_at && (
                    <p className="text-[10px] text-stone-400 mt-0.5">
                      {new Date(r.created_at).toLocaleDateString('tr-TR', {
                        day: 'numeric', month: 'long', year: 'numeric',
                      })}
                    </p>
                  )}
                </div>
              </div>
              <a
                href={apiClient.downloadUrl(r.job_id)}
                className="flex-shrink-0 inline-flex items-center gap-2 px-3 py-1.5 border border-fenlife-orange text-fenlife-orange text-xs font-semibold rounded-md hover:bg-fenlife-orange-soft transition-colors"
              >
                <Download size={14} />
                İndir
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
