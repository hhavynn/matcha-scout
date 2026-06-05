import { IconDrop } from "@/components/Icons";

export default function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16 px-6 text-center">
      <div
        className="flex items-center justify-center rounded-full"
        style={{
          width: 60, height: 60,
          background: "#f3e8d6",
          color: "#93623c",
          boxShadow: "inset 0 0 0 1px rgba(169,119,78,0.25)",
        }}
      >
        <IconDrop size={26} />
      </div>
      <div className="ms-serif" style={{ fontSize: 21, color: "#2a3124" }}>
        That pour didn&apos;t land
      </div>
      <p style={{ fontSize: 14, color: "#585e4d", margin: 0, maxWidth: 320, lineHeight: 1.6 }}>
        {message}
      </p>
      {onRetry && (
        <button className="ms-btn ms-btn-ghost ms-btn-sm" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}
