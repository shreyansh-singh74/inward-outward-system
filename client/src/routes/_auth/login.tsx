import { createFileRoute } from "@tanstack/react-router";
import SignInForm from "@/features/auth/components/login-form";
export const Route = createFileRoute("/_auth/login")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div className="w-full flex-grow mt-4">
      <SignInForm />
    </div>
  );
}
