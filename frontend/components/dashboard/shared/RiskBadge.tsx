import type { RiskResult } from '@/lib/types';

interface RiskBadgeProps {
  risk: RiskResult;
}

export function RiskBadge({ risk }: RiskBadgeProps) {
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
      style={{ backgroundColor: risk.color + '15', color: risk.color }}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: risk.color }} />
      {risk.label}
    </span>
  );
}
