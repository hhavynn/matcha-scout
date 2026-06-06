import ErrorState from "@/components/ErrorState";
import { getReviewTargets } from "@/lib/api";
import ReviewTargetsClient from "./ReviewTargetsClient";

export const dynamic = "force-dynamic";

export default async function ReviewPage() {
  let targets = [] as Awaited<ReturnType<typeof getReviewTargets>>;
  let errorMsg: string | null = null;

  try {
    targets = await getReviewTargets(undefined, 100, 1);
  } catch (err) {
    errorMsg = err instanceof Error ? err.message : "Could not load review targets.";
  }

  if (errorMsg) {
    return (
      <div style={{ maxWidth: 920, margin: "0 auto", padding: "30px 20px" }}>
        <ErrorState message={errorMsg} />
        <p className="text-center text-sm mt-2" style={{ color: "#8c8a78" }}>
          Refresh the page to try again.
        </p>
      </div>
    );
  }

  return <ReviewTargetsClient targets={targets} />;
}
