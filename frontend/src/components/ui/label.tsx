import React from 'react';

export interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  children: React.ReactNode;
  className?: string;
}

export const Label: React.FC<LabelProps> = ({ children, className = '', ...props }) => (
  <label className={`block text-sm font-medium text-teen-purple-700 ${className}`} {...props}>
    {children}
  </label>
);

export default Label; 