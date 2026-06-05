export default function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
      <p className="text-red-600 font-medium">Something went wrong</p>
      <p className="text-sm text-gray-600 max-w-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-sm text-green-700 underline hover:text-green-900"
        >
          Try again
        </button>
      )}
    </div>
  );
}
