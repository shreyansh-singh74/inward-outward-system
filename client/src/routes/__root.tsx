import {
  createRootRoute,
  Outlet,
  redirect,
  useLoaderData,
} from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/router-devtools";
import { userAtom } from "@/lib/atoms";
import { useSetAtom } from "jotai";
import { Toaster } from "@/components/ui/sonner";
export const Route = createRootRoute({
  loader: async () => {
    const res = await fetch("/api/authenticate");
    const data = await res.json();
    return data;
  },
  component: function Component() {
    const data = useLoaderData({ from: "__root__" });
    const setAtom = useSetAtom(userAtom);
    console.log(data);
    if (data.error && data.error === "user is not authorized") {
      return redirect({
        to: "/login",
      });
    }
    setAtom(data.user);
    return (
      <>
        <Outlet />
        <TanStackRouterDevtools />
        <Toaster />
      </>
    );
  },
});
