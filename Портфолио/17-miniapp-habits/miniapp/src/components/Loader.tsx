export function Loader({ label = 'Загрузка…' }: { label?: string }) {
  return (
    <div className="loader" role="status" aria-live="polite">
      <div className="loader__spinner" />
      <span className="loader__label">{label}</span>
    </div>
  );
}
