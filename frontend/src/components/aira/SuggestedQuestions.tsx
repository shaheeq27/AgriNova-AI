import React from 'react';
import { CloudLightning, Sprout, CloudRain, ShieldAlert } from 'lucide-react';
import Image from 'next/image';

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

export function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  const suggestions = [
    {
      icon: <Sprout size={16} className="text-[#ADFF00]" />,
      title: "What should I do today?",
      question: "What should I do today for my crops?"
    },
    {
      icon: <CloudRain size={16} className="text-[#ADFF00]" />,
      title: "Should I irrigate my crop?",
      question: "Should I irrigate my crop today based on the weather?"
    },
    {
      icon: <ShieldAlert size={16} className="text-[#ADFF00]" />,
      title: "Why are my leaves yellow?",
      question: "Why are the leaves on my crop turning yellow?"
    },
    {
      icon: <CloudLightning size={16} className="text-[#ADFF00]" />,
      title: "What weather risks should I watch?",
      question: "What weather risks should I watch out for this week?"
    }
  ];

  return (
    <div className="w-full max-w-[720px] mx-auto flex flex-col items-center gap-8 px-4">
      {/* Header Block */}
      <div className="flex flex-col items-center gap-3 text-center">
        {/* Avatar */}
        <div className="w-[80px] h-[80px] rounded-full bg-[#1F201F] border border-[#ADFF00]/20 flex items-center justify-center relative shadow-[0_0_15px_rgba(173,255,0,0.06)] overflow-hidden flex-shrink-0">
          <Image 
            src="/aira-icon.jpg" 
            alt="Aira Icon" 
            fill 
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 rounded-full bg-[#ADFF00]/5 animate-[pulse_3s_ease-in-out_infinite] pointer-events-none" />
        </div>
        
        {/* Text */}
        <div className="flex flex-col gap-1 items-center">
          <h2 className="text-[24px] font-semibold tracking-tight text-white">Meet Aira</h2>
          <p className="text-[14px] text-[#C4C8C1] font-medium">
            Your AI Agronomist for AgriNova.
          </p>
          <p className="text-[14px] text-[#8D928C] max-w-[400px]">
            Ask me about your farm, crops, weather, irrigation and more.
          </p>
        </div>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-[700px]">
        {suggestions.map((s, i) => (
          <button
            key={i}
            onClick={() => onSelect(s.question)}
            className="group flex items-center gap-3 px-4 rounded-[14px] bg-[#1B1C1B] border border-white/5 hover:border-[#ADFF00]/30 hover:bg-[#2A2A29] hover:shadow-[0_4px_12px_rgba(0,0,0,0.2)] transition-all duration-200 text-left h-[54px] w-full"
          >
            <div className="w-8 h-8 rounded-full bg-[#131412] border border-white/5 flex items-center justify-center flex-shrink-0 group-hover:bg-[#1B1C1B] transition-colors duration-200 shadow-sm">
              {s.icon}
            </div>
            <div className="flex-1 min-w-0">
              <span className="text-[14px] font-medium text-[#E4E2E0] group-hover:text-white transition-colors block truncate">
                {s.title}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
