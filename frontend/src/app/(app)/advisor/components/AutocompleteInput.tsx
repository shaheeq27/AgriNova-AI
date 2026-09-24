import React, { useState, useRef, useEffect } from 'react';

export interface AutocompleteOption {
  label: string;
  value: string;
  description?: string;
}

interface AutocompleteInputProps {
  label: string;
  icon: string | React.ReactNode;
  subtitle?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  options: AutocompleteOption[];
  onSelectOption?: (option: AutocompleteOption) => void;
  allowFreeText?: boolean;
}

export function AutocompleteInput({
  label,
  icon,
  subtitle,
  placeholder,
  value,
  onChange,
  options,
  onSelectOption,
  allowFreeText = false
}: AutocompleteInputProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) {
      if (!allowFreeText) {
        const matched = options.find(o => o.value === value);
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setInputValue(matched ? matched.label : value);
      } else {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setInputValue(value);
      }
    }
  }, [value, options, isOpen, allowFreeText]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredOptions = options.filter(opt =>
    opt.label.toLowerCase().includes(inputValue.toLowerCase()) ||
    (opt.description && opt.description.toLowerCase().includes(inputValue.toLowerCase()))
  );

  const handleInputChange = (val: string) => {
    setInputValue(val);
    setIsOpen(true);
    onChange(allowFreeText ? val : '');
  };

  const handleSelect = (option: AutocompleteOption) => {
    setInputValue(option.label);
    onChange(allowFreeText ? option.label : option.value);
    setIsOpen(false);
    if (onSelectOption) {
      onSelectOption(option);
    }
  };

  const showDropdown = isOpen && (filteredOptions.length > 0 || !allowFreeText);

  return (
    <div className="flex flex-col" ref={wrapperRef} style={{ fontFamily: 'var(--font-sans, system-ui, sans-serif)' }}>
      <label className="flex items-center gap-2 font-bold text-[16px] mb-[6px] tracking-wide" style={{ color: '#4EE86A' }}>
        <span>{icon}</span> {label}
      </label>
      {subtitle && <p className="text-[14px] mb-[8px]" style={{ color: '#9CA3AF' }}>{subtitle}</p>}

      <div className="relative w-full">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => handleInputChange(e.target.value)}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          className="w-full outline-none transition-all duration-200 border rounded-[16px]"
          style={{
            backgroundColor: 'rgba(20, 35, 24, 0.8)',
            borderColor: '#243A29',
            color: '#FFFFFF',
            fontSize: '18px',
            height: '64px',
            padding: '0 24px',
            boxShadow: 'inset 0 4px 6px rgba(0,0,0,0.2)'
          }}
          onMouseEnter={(e) => {
            if (document.activeElement !== e.target) {
              e.currentTarget.style.borderColor = '#324F38';
            }
          }}
          onMouseLeave={(e) => {
            if (document.activeElement !== e.target) {
              e.currentTarget.style.borderColor = '#243A29';
            }
          }}
          onFocusCapture={(e) => {
            e.target.style.borderColor = '#4EE86A';
            e.target.style.boxShadow = '0 0 0 1px #4EE86A, 0 0 12px rgba(78,232,106,0.15), inset 0 2px 4px rgba(0,0,0,0.2)';
          }}
          onBlurCapture={(e) => {
            e.target.style.borderColor = '#243A29';
            e.target.style.boxShadow = 'inset 0 4px 6px rgba(0,0,0,0.2)';
          }}
        />

        {showDropdown && (
          <div
            className="absolute z-50 w-full mt-3 rounded-[16px] shadow-[0_20px_40px_rgba(0,0,0,0.6)] overflow-y-auto border"
            style={{
              backgroundColor: '#0F1A13',
              borderColor: '#243A29',
              maxHeight: '300px'
            }}
          >
            {filteredOptions.length > 0 ? (
              <ul className="py-2">
                {filteredOptions.map((opt, idx) => (
                  <li
                    key={idx}
                    onClick={() => handleSelect(opt)}
                    className="px-6 py-4 cursor-pointer flex flex-col transition-colors border-b last:border-0"
                    style={{ borderColor: '#192B1D' }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#182B1E'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <span className="font-bold text-[16px]" style={{ color: '#FFFFFF' }}>{opt.label}</span>
                    {opt.description && <span className="text-[14px] mt-1" style={{ color: '#9CA3AF' }}>{opt.description}</span>}
                  </li>
                ))}
              </ul>
            ) : (
              !allowFreeText && <div className="px-6 py-5 text-[15px]" style={{ color: '#9CA3AF' }}>No matches found</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
