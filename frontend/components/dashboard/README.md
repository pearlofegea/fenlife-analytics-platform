# Dashboard Components

Mevcut `fenlife-dashboard.jsx` dosyasını bu klasöre `FenlifeDashboard.tsx`
olarak yerleştirin. İçerik değişikliği gerektirmez — sadece:

1. Dosya uzantısını `.tsx` yapın
2. En başa `'use client';` ekleyin (zaten state kullanıyor)
3. Sonra `app/dashboard/page.tsx`'te import edin:

```tsx
import FenlifeDashboard from '@/components/dashboard/FenlifeDashboard';

export default function DashboardPage() {
  return <FenlifeDashboard />;
}
```

Bu klasörde ileride bölünmüş bileşenler olacak:
- `StudentCard.tsx`
- `OverviewTab.tsx`
- `TrendTab.tsx`
- `DifficultyTab.tsx`
- `TopicsTab.tsx`
- `ActionsTab.tsx`
