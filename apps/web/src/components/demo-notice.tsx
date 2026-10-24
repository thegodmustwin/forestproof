import { demoMode } from "@/lib/demo";

export function DemoNotice() {
  return (
    <aside className="notice" role="note">
      <span aria-hidden="true">⚑</span>
      <span><b>{demoMode.label}.</b> {demoMode.description}</span>
    </aside>
  );
}
