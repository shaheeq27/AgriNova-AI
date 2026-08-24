import React from 'react';
import Image from 'next/image';
import { Bot, MapPin, Leaf, Menu, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { FarmData } from '@/lib/api';
import { SidebarState } from '@/app/(app)/aira/page';

interface AiraHeaderProps {
  activeFarm: FarmData | undefined;
  onToggleMobileSidebar: () => void;
  desktopState: SidebarState;
  onCycleDesktopSidebar: () => void;
}

export function AiraHeader({ activeFarm, onToggleMobileSidebar, desktopState, onCycleDesktopSidebar }: AiraHeaderProps) {
  const isExpanded = desktopState === 'expanded';

  return (
    <div className="flex items-center justify-between px-4 md:px-6 border-b border-white/5 bg-[#131412] h-[68px] min-h-[68px] flex-shrink-0 relative z-20">
      <div className="flex items-center gap-3">
        {/* Mobile menu toggle */}
        <button 
          onClick={onToggleMobileSidebar}
          className="md:hidden p-2 -ml-2 text-[#C4C8C1] hover:text-white"
        >
          <Menu size={24} />
        </button>

        {/* Desktop Sidebar Toggle on Left */}
        <button 
          onClick={onCycleDesktopSidebar}
          title={isExpanded ? "Collapse sidebar" : "Expand sidebar"}
          className="hidden md:flex p-2 text-[#8D928C] hover:text-white transition-colors border border-white/5 bg-[#1B1C1B] rounded-lg mr-1"
        >
          {isExpanded ? <PanelLeftClose size={20} /> : <PanelLeftOpen size={20} />}
        </button>

        <div className="w-[32px] h-[32px] md:w-[36px] md:h-[36px] rounded-full bg-[#1F201F] border border-[#ADFF00]/20 flex-shrink-0 overflow-hidden relative shadow-[0_0_10px_rgba(173,255,0,0.1)]">
          <Image 
            src="/aira-icon.jpg" 
            alt="Aira Icon" 
            fill 
            className="object-cover"
          />
        </div>
        <div className="flex flex-col justify-center mt-0.5">
          <h2 className="text-[18px] md:text-[20px] font-semibold text-white m-0 leading-none">Aira</h2>
          <p className="type-label-caps text-[#8D928C] m-0 tracking-[0.08em] text-[10px] mt-1">AI AGRONOMIST</p>
        </div>
      </div>

      <div className="flex items-center gap-4 mt-4 sm:mt-0">
        {activeFarm && (
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4 bg-[#131412] px-4 py-2 rounded-lg border border-white/5">
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
    </div>
  );
}
