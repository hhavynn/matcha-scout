/* Shared icon components used across the app */
interface IconProps {
  size?: number;
  color?: string;
  stroke?: number;
}

function Ico({ size = 20, color = "currentColor", stroke = 1.7, children }: IconProps & { children: React.ReactNode }) {
  return (
    <svg
      width={size} height={size} viewBox="0 0 20 20"
      fill="none" stroke={color} strokeWidth={stroke}
      strokeLinecap="round" strokeLinejoin="round"
      style={{ display: "block", flexShrink: 0 }}
    >
      {children}
    </svg>
  );
}

export function IconSpark({ size = 16, color = "currentColor" }: IconProps) {
  return <Ico size={size} color={color}><path d="M10 3c.7 3.2 1.8 4.3 5 5-3.2.7-4.3 1.8-5 5-.7-3.2-1.8-4.3-5-5 3.2-.7 4.3-1.8 5-5z" /></Ico>;
}
export function IconCheck({ size = 16, color = "currentColor" }: IconProps) {
  return <Ico size={size} color={color}><path d="M4 10.5l4 4 8-9" /></Ico>;
}
export function IconArrow({ size = 16, color = "currentColor" }: IconProps) {
  return <Ico size={size} color={color}><line x1="3" y1="10" x2="16" y2="10" /><path d="M11 5l5 5-5 5" /></Ico>;
}
export function IconBack({ size = 16, color = "currentColor" }: IconProps) {
  return <Ico size={size} color={color}><path d="M12 5l-5 5 5 5" /></Ico>;
}
export function IconLeaf({ size = 20, color = "currentColor" }: IconProps) {
  return <Ico size={size} color={color}><path d="M16 4C8 4 4 8 4 16c8 0 12-4 12-12zM7 13c3-1 5-3 6-6" /></Ico>;
}
export function IconDrop({ size = 20, color = "currentColor" }: IconProps) {
  return <Ico size={size} color={color}><path d="M10 3.5s5 5.5 5 8.5a5 5 0 11-10 0c0-3 5-8.5 5-8.5z" /></Ico>;
}
export function IconSearch({ size = 18, color = "currentColor" }: IconProps) {
  return <Ico size={size} color={color}><circle cx="8" cy="8" r="5.2" /><line x1="12" y1="12" x2="16.5" y2="16.5" /></Ico>;
}
export function IconFilter({ size = 18, color = "currentColor" }: IconProps) {
  return <Ico size={size} color={color}><line x1="3" y1="6" x2="17" y2="6" /><line x1="6" y1="10" x2="14" y2="10" /><line x1="8.5" y1="14" x2="11.5" y2="14" /></Ico>;
}
export function IconStar({ size = 14, color = "currentColor" }: IconProps) {
  return <Ico size={size} color={color}><path d="M10 3l2.1 4.4 4.9.6-3.6 3.3 1 4.7L10 13.8 5.6 16l1-4.7L3 8l4.9-.6L10 3z" /></Ico>;
}
