export default function LoadingState({ message = "Steeping your matches…" }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-5 py-16 text-center px-6">
      {/* Matcha ring spinner with inner dot */}
      <div style={{ position: "relative", width: 52, height: 52 }}>
        <div
          style={{
            position: "absolute", inset: 0, borderRadius: 999,
            border: "3px solid #e7eddc",
            borderTopColor: "#56703f",
            animation: "ms-spin 0.9s linear infinite",
          }}
        />
        <div
          style={{
            position: "absolute", inset: 16, borderRadius: 999,
            background: "#5f7850", opacity: 0.5,
          }}
        />
      </div>
      <p style={{ fontSize: 14.5, color: "#585e4d", margin: 0 }}>{message}</p>
    </div>
  );
}
