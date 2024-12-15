import { createFileRoute, useParams } from "@tanstack/react-router";
import ResetPasswordForm from "@/features/auth/components/reset-password-form";
export const Route = createFileRoute("/_auth/reset-password/$token")({
  component: RouteComponent,
});

function RouteComponent() {
  const { token } = useParams({ from: "/_auth/reset-password/$token" });
  console.log(token);
  return (
    <div className="w-full mt-4 flex-grow">
      <ResetPasswordForm />
    </div>
  );
}
