export const Tabs: React.FC<{ className?: string; children: React.ReactNode }> = ({ className = '', children }) => {
  return <div className={className}>{children}</div>;
};

export const TabsList: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`flex space-x-2 ${className}`}>{children}</div>
);

export const TabsTrigger: React.FC<{ value: string; children: React.ReactNode; className?: string }> = ({ value, children, className = '', ...props }) => (
  <button type="button" className={`px-4 py-2 rounded bg-teen-purple-100 text-teen-purple-700 font-medium ${className}`} {...props}>{children}</button>
);

export const TabsContent: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={className}>{children}</div>
);

export default Tabs; 