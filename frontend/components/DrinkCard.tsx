import Link from "next/link";
import type { Drink } from "@/lib/types";

interface Props {
  drink: Drink;
  cafeName?: string;
}

export default function DrinkCard({ drink, cafeName }: Props) {
  return (
    <Link
      href={`/drinks/${drink.id}`}
      className="block bg-white rounded-2xl shadow-sm border border-green-100 p-4 hover:shadow-md hover:border-green-200 transition-all"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-semibold text-green-900 leading-snug">{drink.name}</h3>
        <span className="text-green-700 font-medium text-sm shrink-0">${drink.price.toFixed(2)}</span>
      </div>

      {cafeName && (
        <p className="text-xs text-green-600 mt-0.5">{cafeName}</p>
      )}

      <p className="text-sm text-gray-600 mt-2 line-clamp-2">{drink.description}</p>

      <div className="mt-3 flex flex-wrap gap-1.5">
        {drink.milk_options.map((m) => (
          <span
            key={m}
            className="text-xs bg-green-50 text-green-700 border border-green-100 rounded-full px-2 py-0.5"
          >
            {m}
          </span>
        ))}
        {drink.is_iced && (
          <span className="text-xs bg-blue-50 text-blue-600 border border-blue-100 rounded-full px-2 py-0.5">
            iced
          </span>
        )}
        {drink.is_hot && (
          <span className="text-xs bg-red-50 text-red-500 border border-red-100 rounded-full px-2 py-0.5">
            hot
          </span>
        )}
      </div>
    </Link>
  );
}
