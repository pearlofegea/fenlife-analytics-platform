'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FileText, X, Loader2, Info, ChevronRight, LayoutDashboard } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { UploadZone } from '@/components/reports/UploadZone';

const RECOMMENDED_MIN = 5;

export default function GenerateReportPage() {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addFiles = (incoming: File[]) => {
    setFiles((prev) => {
      const existing = new Set(prev.map((f) => f.name + f.size));
      const unique = incoming.filter((f) => !existing.has(f.name + f.size));
      return [...prev, ...unique];
    });
    setError(null);
  };

  const removeFile = (idx: number) => setFiles((prev) => prev.filter((_, i) => i !== idx));

  const handleSubmit = async () => {
    if (files.length === 0) {
      setError('En az bir PDF dosyası seçin.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.createReport(files);
      router.push(`/reports/preview/${response.job_id}`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const belowRecommended = files.length > 0 && files.length < RECOMMENDED_MIN;

  return (
    <main className="min-h-screen p-6 md:p-8">
      <div className="max-w-3xl mx-auto">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-xs text-stone-400 mb-6">
          <Link href="/dashboard" className="flex items-center gap-1 hover:text-stone-600 transition-colors">
            <LayoutDashboard size={12} />
            Dashboard
          </Link>
          <ChevronRight size={12} />
          <span className="text-stone-700 font-medium">Rapor Üret</span>
        </nav>

        <h1 className="font-serif text-3xl font-bold text-fenlife-blue mb-2">Rapor Üret</h1>
        <p className="text-stone-600 mb-8">
          Öğrenciye ait sınav sonucu PDF dosyalarını yükleyin. Sistem formatı tanır, verileri
          normalize eder ve FENlife markalı analiz raporu oluşturur.
        </p>

        <UploadZone
          onFilesAdded={addFiles}
          label="PDF dosyalarını seçin veya sürükleyin"
          sublabel="PDF formatı · tek veya çok dosya"
        />

        {files.length > 0 && (
          <div className="mt-5 space-y-2">
            {files.map((f, idx) => (
              <div
                key={idx}
                className="flex items-center gap-3 p-3 bg-white border border-stone-200 rounded-md"
              >
                <FileText className="w-5 h-5 text-fenlife-blue flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-stone-900 truncate">{f.name}</p>
                  <p className="text-xs text-stone-500">{(f.size / 1024).toFixed(1)} KB</p>
                </div>
                <button
                  onClick={() => removeFile(idx)}
                  className="p-1 hover:bg-stone-100 rounded"
                  aria-label="Kaldır"
                >
                  <X className="w-4 h-4 text-stone-400" />
                </button>
              </div>
            ))}
          </div>
        )}

        {belowRecommended && (
          <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-md flex items-start gap-2 text-sm text-amber-800">
            <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>
              Daha güvenilir analiz, gelişim takibi ve eğilim yorumları için en az {RECOMMENDED_MIN} sınav
              verisi önerilir. Az veriyle de rapor oluşturulabilir; ancak karşılaştırmalı içgörüler
              sınırlı kalabilir.
            </span>
          </div>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="mt-6 flex items-center justify-between">
          <p className="text-sm text-stone-600">
            <strong className="font-mono">{files.length}</strong>{' '}
            dosya seçildi
          </p>
          <button
            onClick={handleSubmit}
            disabled={loading || files.length === 0}
            className="px-6 py-2.5 bg-fenlife-blue text-white font-semibold rounded-md hover:bg-fenlife-blue-dark disabled:bg-stone-300 disabled:cursor-not-allowed transition-colors inline-flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                İşleniyor...
              </>
            ) : (
              'Raporu Üret'
            )}
          </button>
        </div>
      </div>
    </main>
  );
}
