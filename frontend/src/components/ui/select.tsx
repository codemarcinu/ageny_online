import React from 'react';

export const Select: React.FC<React.SelectHTMLAttributes<HTMLSelectElement> & { onValueChange?: (value: string) => void }> = ({ children, className = '', onValueChange, ...props }) => (
  <select className={`border border-teen-purple-300 rounded px-3 py-2 ${className}`}
    onChange={e => onValueChange ? onValueChange(e.target.value) : props.onChange?.(e as any)}
    {...props}
  >
    {children}
  </select>
);

export const SelectContent: React.FC<{ children: React.ReactNode }> = ({ children }) => <>{children}</>;
export const SelectItem: React.FC<{ children: React.ReactNode; value?: string }> = ({ children, ...props }) => <option {...props}>{children}</option>;
export const SelectTrigger: React.FC<{ children: React.ReactNode }> = ({ children }) => <>{children}</>;
export const SelectValue: React.FC<{ children?: React.ReactNode }> = ({ children }) => <>{children}</>;

export default Select; 