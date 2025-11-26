import React from 'react';

interface SliderProps {
  label: string;
  value: number;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  min?: number;
  max?: number;
  step?: number;
  displayValue?: number | string;
  displaySuffix?: string;
}

const Slider: React.FC<SliderProps> = ({ label, value, onChange, min = 0, max = 100, step = 1, displayValue, displaySuffix = '' }) => {
  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-1">
        <label className="block text-sm font-medium text-gray-700">{label}</label>
        <span className="text-sm font-mono text-gray-500">
          {displayValue !== undefined ? displayValue : value}{displaySuffix}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={onChange}
        className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb"
      />
      <style>{`
        .slider-thumb::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 14px;
          height: 14px;
          background: #1f2937;
          cursor: pointer;
          border-radius: 50%;
          transition: background .2s;
        }
        .slider-thumb:hover::-webkit-slider-thumb {
          background: #000;
        }
        .slider-thumb::-moz-range-thumb {
          width: 14px;
          height: 14px;
          background: #1f2937;
          cursor: pointer;
          border-radius: 50%;
          border: none;
          transition: background .2s;
        }
        .slider-thumb:hover::-moz-range-thumb {
          background: #000;
        }
      `}</style>
    </div>
  );
};

export default Slider;
