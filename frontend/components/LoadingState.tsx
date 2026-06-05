export default function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 text-green-700">
      <div className="w-8 h-8 border-2 border-green-300 border-t-green-600 rounded-full animate-spin" />
      <p className="text-sm">{message}</p>
    </div>
  );
}
