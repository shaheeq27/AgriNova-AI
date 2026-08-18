import React from 'react';
import { Bot, Sprout, CloudRain, ShieldAlert } from 'lucide-react';

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

export function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  const suggestions = [
    {
      icon: <Sprout size={20} className="text-[#ADFF00]" />,
      title: "What should I do today?",
      question: "What should I do today for my crops?"
    },
    {
      icon: <CloudRain size={20} className="text-[#ADFF00]" />,
      title: "Should I irrigate my crop?",
      question: "Should I irrigate my crop today based on the weather?"
    },
    {
      icon: <ShieldAlert size={20} className="text-[#ADFF00]" />,
      title: "Why are my leaves yellow?",
      question: "Why are the leaves on my crop turning yellow?"
    },
    {
      icon: <Bot size={20} className="text-[#ADFF00]" />,
      title: "What weather risks should I watch?",
      question: "What weather risks should I watch out for this week?"
    }
  ];

  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col items-center justify-center mt-12 mb-8 px-4">
      <div className="w-16 h-16 rounded-2xl bg-[#1F201F] border border-[#ADFF00]/30 flex items-center justify-center text-[#ADFF00] mb-6 relative">
        <div className="absolute inset-0 rounded-2xl bg-[#ADFF00]/10 animate-ping opacity-20" />
        <Bot size={32} strokeWidth={1.5} />
      </div>
      
      <h2 className="type-headline-md mb-2 text-center">Meet Aira</h2>
      <p className="type-body-md text-[#8D928C] text-center mb-10 max-w-md">
        Your AI Agronomist for AgriNova. Ask me about your farm, crops, weather, irrigation and more.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
        {suggestions.map((s, i) => (
          <button
            key={i}
            onClick={() => onSelect(s.question)}
            className="group flex flex-col items-start text-left p-4 rounded-xl bg-[#1B1C1B] border border-white/5 hover:border-[#ADFF00]/40 transition-colors"
          >
            <div className="mb-3 opacity-80 group-hover:opacity-100 transition-opacity">
              {s.icon}
            </div>
            <span className="type-body-sm font-medium text-[#E4E2E0] group-hover:text-white transition-colors">
              {s.title}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
