'use client';

import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { Download, CheckCircle2, Loader2, AlertCircle, ChevronLeft, ChevronRight, FileText, LayoutDashboard } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import type { ReportStatusResponse } from '@/lib/types';

const POLL_INTERVAL_MS = 3000;

export default function ReportPreviewPage({ params }: { params: { jobId: string } }) {
  const { jobId } = params;
  const [data, setData] = useState<ReportStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const poll = async () => {
      try {
        const result = await apiClient.getReportStatus(jobId);
        setData(result);
        if (result.status === 'completed' || result.status === 'failed') {
          if (intervalRef.current) clearInterval(intervalRef.current);
        }
      } catch (err) {
        setError((err as Error).message);
        if (intervalRef.current) clearInterval(intervalRef.current);
      }
    };

    poll();
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [jobId]);

  const isLoading = !data && !error;
  const isProcessing = data?.status === 'processing';
  const isCompleted = data?.status === 'completed';
  const isFailed = data?.status === 'failed' || !!error;

  return (
    <main className="min-h-screen p-6 md:p-8">
      <div className="max-w-3xl mx-auto">
        {/* Breadcrumb + geri */}
        <div className="flex items-center justify-between mb-6">
          <nav className="flex items-center gap-1.5 text-xs text-stone-400">
            <Link href="/dashboard" className="flex items-center gap-1 hover:text-stone-600 transition-colors">
              <LayoutDashboard size={12} />
              Dashboard
            </Link>
            <ChevronRight size={12} />
            <Link href="/reports" className="hover:text-stone-600 transition-colors">
              Raporlar
            </Link>
            <ChevronRight size={12} />
            <span className="text-stone-700 font-medium">Rapor Önizleme</span>
          </nav>
          <Link
            href="/reports"
            className="flex items-center gap-1.5 text-xs text-stone-500 hover:text-stone-700 transition-colors"
          >
            <ChevronLeft size={14} />
            Raporlara Dön
          </Link>
        </div>

        <div className="bg-white border border-stone-200 rounded-lg p-8">
          <div className="flex items-center gap-3 mb-6">
            {(isLoading || isProcessing) && (
              <Loader2 className="w-6 h-6 text-fenlife-blue animate-spin" />
            )}
            {isCompleted && <CheckCircle2 className="w-6 h-6 text-green-600" />}
            {isFailed && <AlertCircle className="w-6 h-6 text-red-500" />}
            <h1 className="font-serif text-2xl font-semibold text-stone-900">
              {isLoading && 'Bağlanıyor...'}
              {isProcessing && 'Rapor hazırlanıyor...'}
              {isCompleted && 'Rapor hazır'}
              {isFailed && 'Hata oluştu'}
            </h1>
          </div>

          <p className="text-[11px] text-stone-400 font-mono mb-6">Job: {jobId}</p>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700 mb-4">
              {error}
            </div>
          )}

          {data && (
            <div className="space-y-2 text-sm">
              {data.student_name && (
                <div className="flex gap-2">
                  <span className="text-stone-500 w-28 flex-shrink-0">Öğrenci</span>
                  <strong className="text-stone-900">{data.student_name}</strong>
                </div>
              )}
              {data.student_grade && (
                <div className="flex gap-2">
                  <span className="text-stone-500 w-28 flex-shrink-0">Sınıf</span>
                  <strong className="text-stone-900">{data.student_grade}</strong>
                </div>
              )}
              {data.exam_count != null && (
                <div className="flex gap-2">
                  <span className="text-stone-500 w-28 flex-shrink-0">Sınav sayısı</span>
                  <strong className="text-stone-900">{data.exam_count}</strong>
                </div>
              )}
              {data.avg_puan != null && (
                <div className="flex gap-2">
                  <span className="text-stone-500 w-28 flex-shrink-0">Ortalama puan</span>
                  <strong className="font-mono text-fenlife-blue">{data.avg_puan.toFixed(1)}</strong>
                </div>
              )}
              {data.risk_level && (
                <div className="flex gap-2">
                  <span className="text-stone-500 w-28 flex-shrink-0">Risk seviyesi</span>
                  <strong className="text-stone-900">{data.risk_level}</strong>
                </div>
              )}
            </div>
          )}

          {isCompleted && (
            <div className="mt-6 flex items-center gap-3 flex-wrap">
              <a
                href={apiClient.downloadUrl(jobId)}
                className="inline-flex items-center gap-2 px-6 py-2.5 bg-fenlife-orange text-white font-semibold rounded-md hover:opacity-90 transition-opacity"
              >
                <Download className="w-4 h-4" />
                DOCX Raporunu İndir
              </a>
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 px-4 py-2.5 border border-stone-200 text-stone-600 text-sm font-medium rounded-md hover:bg-stone-50 transition-colors"
              >
                <LayoutDashboard size={15} />
                Dashboard&apos;a Git
              </Link>
            </div>
          )}

          {isProcessing && (
            <p className="mt-4 text-xs text-stone-500">
              Rapor işleniyor — her {POLL_INTERVAL_MS / 1000} saniyede bir kontrol ediliyor...
            </p>
          )}
        </div>

        {/* Tamamlandıysa raporlar listesine hızlı bağlantı */}
        {isCompleted && (
          <div className="mt-4 p-4 bg-white border border-stone-200 rounded-lg flex items-center gap-3">
            <FileText size={18} className="text-stone-400 flex-shrink-0" />
            <div className="flex-1 text-sm text-stone-600">
              Tüm tamamlanmış raporları görmek için{' '}
              <Link href="/reports" className="text-fenlife-blue font-semibold hover:underline">
                Raporlar
              </Link>{' '}
              sayfasına gidin.
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
