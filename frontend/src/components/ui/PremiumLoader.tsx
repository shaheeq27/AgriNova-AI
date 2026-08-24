'use client';

import React, { useState, useEffect } from 'react';

interface PremiumLoaderProps {
  message: string;
}

export function PremiumLoader({ message }: PremiumLoaderProps) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setShow(true), 150);
    return () => clearTimeout(t);
  }, []);

  if (!show) return <div className="flex-1 min-h-[50vh]" />;

  return (
    <div className="flex-1 flex flex-col items-center justify-center min-h-[50vh] animate-fade-in">
       <div className="text-[#8D928C] type-label-caps tracking-widest mb-6 uppercase">{message}</div>
       <div className="w-48 h-[2px] bg-white/5 relative overflow-hidden rounded-full">
         <div className="absolute top-0 bottom-0 left-0 bg-[#ADFF00] w-1/3 rounded-full shadow-[0_0_10px_#ADFF00]" style={{ animation: 'shimmer 1.5s ease-in-out infinite' }} />
       </div>
    </div>
  );
}
