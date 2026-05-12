'use client';

import { useRef, useState } from 'react';
import { Upload } from 'lucide-react';

interface UploadZoneProps {
  onFilesAdded: (files: File[]) => void;
  accept?: string;
  multiple?: boolean;
  label?: string;
  sublabel?: string;
}

export function UploadZone({
  onFilesAdded,
  accept = '.pdf',
  multiple = true,
  label = 'PDF dosyalarını seçin veya bırakın',
  sublabel = 'Tek veya çok dosya · PDF formatı',
}: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList) return;
    const pdfs = Array.from(fileList).filter(
      (f) => f.type === 'application/pdf' || f.name.endsWith('.pdf'),
    );
    if (pdfs.length > 0) onFilesAdded(pdfs);
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => inputRef.current?.click()}
      onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleFiles(e.dataTransfer.files); }}
      className={`border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-colors select-none ${
        isDragging
          ? 'border-fenlife-blue bg-[#1B5E8C]/5'
          : 'border-stone-300 hover:border-fenlife-blue'
      }`}
    >
      <Upload
        className={`w-10 h-10 mx-auto mb-3 transition-colors ${
          isDragging ? 'text-fenlife-blue' : 'text-stone-400'
        }`}
      />
      <p className="font-semibold text-stone-900">{label}</p>
      <p className="text-sm text-stone-500 mt-1">{sublabel}</p>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        className="hidden"
        onChange={(e) => {
          handleFiles(e.target.files);
          e.target.value = '';   // aynı dosyanın tekrar seçilebilmesi için input'u sıfırla
        }}
      />
    </div>
  );
}
