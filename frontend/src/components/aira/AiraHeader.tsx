import React from 'react';
import { Bot, MapPin, Leaf, Menu } from 'lucide-react';
import { FarmData } from '@/lib/api';

interface AiraHeaderProps {
  activeFarm: FarmData | undefined;
  onToggleSidebar: () => void;
}

export function AiraHeader({ activeFarm, onToggleSidebar }: AiraHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 sm:p-6 border-b border-white/5 bg-[#1B1C1B]/80 backdrop-blur-md sticky top-0 z-20">
      <div className="flex items-center gap-4">
        <button 
          onClick={onToggleSidebar}
          className="md:hidden p-2 -ml-2 text-[#C4C8C1] hover:text-white"
        >
          <Menu size={24} />
        </button>
        <div className="w-10 h-10 rounded-xl bg-[#1F201F] border border-[#ADFF00]/20 flex items-center justify-center text-[#ADFF00]">
          <Bot size={20} strokeWidth={1.75} />
        </div>
        <div>
          <h2 className="type-headline-sm m-0 leading-tight">Aira</h2>
          <p className="type-label-caps text-[#8D928C] m-0">AI Agronomist</p>
        </div>
      </div>

      {activeFarm && (
        <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4 bg-[#131412] px-4 py-2 rounded-lg border border-white/5">
          <div className="flex items-center gap-2 text-[#C4C8C1]">
            <MapPin size={14} className="text-[#ADFF00]/70" />
            <span className="text-sm font-medium">{activeFarm.name}</span>
          </div>
          {activeFarm.crops && activeFarm.crops.length > 0 && (
            <>
              <div className="hidden sm:block w-px h-4 bg-white/10" />
              <div className="flex items-center gap-2 text-[#C4C8C1]">
                <Leaf size={14} className="text-[#ADFF00]/70" />
                <span className="text-sm">
                  {activeFarm.crops.map(c => c.crop_name).join(', ')}
                </span>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
