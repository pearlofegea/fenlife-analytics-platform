import { type LucideIcon } from 'lucide-react';

interface StatCardProps {
  icon?: LucideIcon;
  label: string;
  value: string | number;
  sublabel?: string;
  accent?: string;
  iconColor?: string;
}

export function StatCard({ icon: Icon, label, value, sublabel, accent, iconColor }: StatCardProps) {
  const color = accent || '#1B5E8C';
  return (
    <div className="bg-white border border-stone-200 rounded-lg p-4 relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-stone-500 font-medium">{label}</p>
          <p
            className="text-2xl font-serif font-semibold mt-1"
            style={{ color, fontVariantNumeric: 'tabular-nums' }}
          >
            {value}
          </p>
          {sublabel && <p className="text-xs text-stone-500 mt-0.5">{sublabel}</p>}
        </div>
        {Icon && (
          <div className="p-2 rounded-md" style={{ backgroundColor: (iconColor || '#1B5E8C') + '15' }}>
            <Icon size={16} style={{ color: iconColor || '#1B5E8C' }} />
          </div>
        )}
      </div>
    </div>
  );
}
