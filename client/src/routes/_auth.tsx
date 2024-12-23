import { createFileRoute, Outlet } from "@tanstack/react-router";
import Logo from "@/assets/tcet_logo_2.png";
export const Route = createFileRoute("/_auth")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div className="w-full h-screen flex flex-col items-center">
      <nav className="flex bg-[#d17a00] w-full justify-between items-center py-2 px-3">
        <img src={Logo} />
        <h1 className="text-xl text-center text-[#ffffff]">
          INWARD OUTWARD SYSTEM
        </h1>
      </nav>
      <Outlet />
    </div>
  );
}
