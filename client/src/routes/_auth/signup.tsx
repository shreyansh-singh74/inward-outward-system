import { createFileRoute } from "@tanstack/react-router";
import SignUpForm from "@/features/auth/components/signup-form";
export const Route = createFileRoute("/_auth/signup")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div className="w-full flex-grow mt-4">
      <SignUpForm />
    </div>
  );
}
