import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  variant?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, className = '', variant, ...props }) => (
  <div className={`inline-block px-3 py-1 rounded-full bg-teen-purple-100 text-teen-purple-700 text-xs font-semibold ${className}`}
    data-variant={variant}
    {...props}
  >
    {children}
  </div>
);

export default Badge; 