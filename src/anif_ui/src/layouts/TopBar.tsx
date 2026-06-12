interface TopBarProps {
  title: string;
  actions?: React.ReactNode;
}

export function TopBar({ title, actions }: TopBarProps) {
  return (
    <header className="h-14 px-6 bg-white border-b border-chrome-200 flex items-center justify-between shrink-0">
      <h1 className="text-sm font-semibold text-chrome-900">{title}</h1>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </header>
  );
}
