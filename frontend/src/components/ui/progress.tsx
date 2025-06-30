import React from 'react';

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
  className?: string;
}

export const Progress: React.FC<ProgressProps> = ({ value, className = '', ...props }) => (
  <div className={`w-full bg-gray-200 rounded-full h-2 ${className}`} {...props}>
    <div
      className="bg-teen-purple-500 h-2 rounded-full"
      style={{ width: `${value}%` }}
    />
  </div>
);

export default Progress; 