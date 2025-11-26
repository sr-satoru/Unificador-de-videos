
import React from 'react';

interface DropdownProps {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  options: string[];
}

const Dropdown: React.FC<DropdownProps> = ({ label, value, onChange, options }) => {
  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <select
        value={value}
        onChange={onChange}
        className="w-full bg-gray-100 border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
      >
        {options.map(option => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Dropdown;