'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, FileUp, Users, FileText, X } from 'lucide-react';

const NAV_ITEMS = [
  { href: '/dashboard',         label: 'Dashboard',   Icon: LayoutDashboard },
  { href: '/reports/generate',  label: 'Rapor Üret',  Icon: FileUp          },
  { href: '/students',          label: 'Öğrenciler',  Icon: Users           },
  { href: '/reports',           label: 'Raporlar',    Icon: FileText        },
];

interface SidebarProps {
  onClose?: () => void;
}

export function Sidebar({ onClose }: SidebarProps) {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (pathname === href) return true;
    // Prefix match: sadece daha spesifik bir nav item yoksa aktif say.
    // Örnek: /reports/generate pathname'indeyken /reports eşleşmesin.
    if (pathname.startsWith(href + '/')) {
      return !NAV_ITEMS.some(
        (item) => item.href !== href && pathname.startsWith(item.href),
      );
    }
    return false;
  };

  return (
    <aside className="flex flex-col h-full bg-white border-r border-stone-200 w-60">
      {/* Logo */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-stone-100">
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-md flex items-center justify-center text-white font-serif font-bold text-lg flex-shrink-0"
            style={{ background: 'linear-gradient(135deg, #1B5E8C 0%, #164A6E 100%)' }}
          >
            F
          </div>
          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="font-serif text-base font-bold text-fenlife-blue leading-none">FENlife</span>
              <span className="text-[9px] uppercase tracking-widest text-fenlife-orange font-semibold">Analytics</span>
            </div>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-stone-100 text-stone-400 lg:hidden"
            aria-label="Menüyü kapat"
          >
            <X size={18} />
          </button>
        )}
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV_ITEMS.map(({ href, label, Icon }) => {
          const active = isActive(href);
          return (
            <Link
              key={href}
              href={href}
              onClick={onClose}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                active
                  ? 'bg-fenlife-blue text-white shadow-sm'
                  : 'text-stone-600 hover:bg-stone-100 hover:text-stone-900'
              }`}
            >
              <Icon size={17} className="flex-shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-stone-100">
        <p className="text-[10px] text-stone-400 uppercase tracking-widest">FENlife Maltepe</p>
        <p className="text-[10px] text-stone-300 mt-0.5">v0.2 — prod hazırlık</p>
      </div>
    </aside>
  );
}
