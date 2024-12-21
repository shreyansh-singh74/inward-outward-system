import {
  createFileRoute,
  useLoaderData,
  useNavigate,
} from "@tanstack/react-router";
import { toast } from "sonner";

export const Route = createFileRoute("/_auth/verify/$token")({
  loader: async ({ params }) => {
    const res = await fetch(`/api/auth/verify/${params.token}`, {
      method: "POST",
    });
    if (res.status !== 200) {
      toast.error("Failed to verify your account");
    }
    const data = await res.json();
    return data;
  },
  component: RouteComponent,
});

function RouteComponent() {
  const loaderData = useLoaderData({ from: "/_auth/verify/$token" });
  console.log(loaderData);
  const navigate = useNavigate();
  if (loaderData?.message === "User is now Authorized") {
    navigate({ to: "/" });
  }
  return (
    <div className="w-full text-2xl font-bold text-center">
      Please wait a minute
    </div>
  );
}
