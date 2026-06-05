import { IconLeaf, IconDrop, IconSearch } from "@/components/Icons";

type IconName = "leaf" | "drop" | "search";

interface Props {
  title: string;
  body: string;
  icon?: IconName;
  action?: React.ReactNode;
}

export default function EmptyState({ title, body, icon = "leaf", action }: Props) {
  const IconComp = icon === "drop" ? IconDrop : icon === "search" ? IconSearch : IconLeaf;

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16 px-6 text-center">
      <div
        className="flex items-center justify-center rounded-full"
        style={{
          width: 60, height: 60,
          background: "#e7eddc",
          color: "#56703f",
          boxShadow: "inset 0 0 0 1px rgba(95,120,80,0.18)",
        }}
      >
        <IconComp size={26} />
      </div>
      <div className="ms-serif" style={{ fontSize: 21, color: "#2a3124" }}>{title}</div>
      <p style={{ fontSize: 14, color: "#585e4d", margin: 0, maxWidth: 320, lineHeight: 1.6 }}>{body}</p>
      {action}
    </div>
  );
}
