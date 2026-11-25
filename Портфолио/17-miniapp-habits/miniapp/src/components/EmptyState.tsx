interface Props {
  icon?: string;
  title: string;
  subtitle?: string;
  action?: { label: string; onClick: () => void };
}

export function EmptyState({ icon = '🌱', title, subtitle, action }: Props) {
  return (
    <div className="empty">
      <div className="empty__icon">{icon}</div>
      <h2 className="empty__title">{title}</h2>
      {subtitle && <p className="empty__subtitle">{subtitle}</p>}
      {action && (
        <button className="btn btn--primary" onClick={action.onClick}>
          {action.label}
        </button>
      )}
    </div>
  );
}
