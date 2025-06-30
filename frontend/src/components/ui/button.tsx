import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  className?: string;
  variant?: string;
  size?: string;
}

export const Button: React.FC<ButtonProps> = ({ children, className = '', variant, size, ...props }) => (
  <button
    className={`px-4 py-2 rounded bg-teen-purple-500 text-white hover:bg-teen-purple-600 transition ${className}`}
    data-variant={variant}
    data-size={size}
    {...props}
  >
    {children}
  </button>
);

export default Button; 