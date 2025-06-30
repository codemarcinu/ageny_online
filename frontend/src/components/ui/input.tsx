import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  className?: string;
}

export const Input: React.FC<InputProps> = ({ className = '', ...props }) => (
  <input
    className={`border border-teen-purple-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teen-purple-500 ${className}`}
    {...props}
  />
);

export default Input; 