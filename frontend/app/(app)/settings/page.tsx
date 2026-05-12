import { Settings } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex items-center gap-2 mb-2">
        <Settings size={22} className="text-fenlife-blue" />
        <h1 className="font-serif text-2xl font-bold text-stone-900">Ayarlar</h1>
      </div>
      <p className="text-sm text-stone-500 mb-8">Sistem yapılandırması ve tercihler</p>

      <div className="space-y-4">
        <div className="bg-white border border-stone-200 rounded-lg p-5">
          <h2 className="font-semibold text-stone-800 mb-1">Kurum</h2>
          <p className="text-sm text-stone-500 mb-3">Raporda görünecek kurum bilgisi</p>
          <div className="flex items-center gap-3">
            <div className="flex-1 px-3 py-2 bg-stone-50 border border-stone-200 rounded-md text-sm text-stone-700 font-medium">
              FENlife Maltepe
            </div>
            <span className="text-xs text-stone-400 italic">Yakında düzenlenebilir</span>
          </div>
        </div>

        <div className="bg-white border border-stone-200 rounded-lg p-5">
          <h2 className="font-semibold text-stone-800 mb-1">Analiz Eşikleri</h2>
          <p className="text-sm text-stone-500 mb-3">Rapor kalitesi için minimum deneme sayıları</p>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="px-3 py-2 bg-stone-50 border border-stone-200 rounded-md">
              <p className="text-xs text-stone-500 mb-0.5">Min. kabul</p>
              <p className="font-mono font-semibold text-stone-800">1 deneme</p>
            </div>
            <div className="px-3 py-2 bg-stone-50 border border-stone-200 rounded-md">
              <p className="text-xs text-stone-500 mb-0.5">Önerilen</p>
              <p className="font-mono font-semibold text-stone-800">5 deneme</p>
            </div>
          </div>
        </div>

        <div className="bg-white border border-stone-200 rounded-lg p-5">
          <h2 className="font-semibold text-stone-800 mb-1">Sistem Bilgisi</h2>
          <div className="space-y-2 text-sm text-stone-600 mt-2">
            <div className="flex justify-between">
              <span>Sürüm</span>
              <span className="font-mono text-stone-800">v0.2</span>
            </div>
            <div className="flex justify-between">
              <span>Backend</span>
              <span className="font-mono text-stone-800">FastAPI + PostgreSQL</span>
            </div>
            <div className="flex justify-between">
              <span>Frontend</span>
              <span className="font-mono text-stone-800">Next.js 14 App Router</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
