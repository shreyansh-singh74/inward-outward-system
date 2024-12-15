import { createFileRoute } from "@tanstack/react-router";
import ForgotPasswordForm from "@/features/auth/components/forgot-password-form";
export const Route = createFileRoute("/_auth/forgot_password_request")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div className="w-full mt-4 flex-grow justify-center items-center">
      <ForgotPasswordForm />
    </div>
  );
}
