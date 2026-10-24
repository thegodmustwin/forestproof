import { CaseWorkspace } from "@/components/case-workspace";

export default function CasePage({ params }: { params: { id: string } }) {
  return <CaseWorkspace id={params.id} />;
}
