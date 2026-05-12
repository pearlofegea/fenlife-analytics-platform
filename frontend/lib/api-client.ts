/**
 * FENlife Backend API client.
 * Tüm FastAPI çağrıları bu dosyadan yapılır.
 */
import type {
  CreateReportResponse,
  ReportStatusResponse,
  DashboardData,
} from '@/lib/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  async healthCheck(): Promise<{ status: string }> {
    const res = await fetch(`${API_URL}/health`);
    if (!res.ok) throw new Error('Backend erişilemiyor');
    return res.json();
  },

  /** Sınav PDF dosyalarını yükle, rapor üretimini başlat (1+ dosya kabul edilir). */
  async createReport(files: File[]): Promise<CreateReportResponse> {
    const formData = new FormData();
    files.forEach((f) => formData.append('files', f));

    const res = await fetch(`${API_URL}/api/reports`, {
      method: 'POST',
      body: formData,
      // Content-Type KASTEN set edilmiyor — browser boundary'yi kendisi yazar
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Bilinmeyen hata' }));
      throw new Error(err.detail || 'Rapor üretimi başarısız');
    }
    return res.json();
  },

  /** Job durumunu sorgula. */
  async getReportStatus(jobId: string): Promise<ReportStatusResponse> {
    const res = await fetch(`${API_URL}/api/reports/${jobId}`);
    if (!res.ok) throw new Error('Job bulunamadı');
    return res.json();
  },

  /** Dashboard verisi — tek öğrenci (job_id ile). */
  async getDashboard(studentId: string): Promise<DashboardData> {
    const res = await fetch(`${API_URL}/api/students/${studentId}/dashboard`);
    if (!res.ok) throw new Error('Dashboard verisi alınamadı');
    return res.json();
  },

  /** Öğrenci listesi. */
  async listStudents(): Promise<{ students: unknown[] }> {
    const res = await fetch(`${API_URL}/api/students`);
    if (!res.ok) throw new Error('Öğrenci listesi alınamadı');
    return res.json();
  },

  /** DOCX indirme URL'i — doğrudan <a href> için. */
  downloadUrl(jobId: string): string {
    return `${API_URL}/api/reports/${jobId}/download`;
  },
};
