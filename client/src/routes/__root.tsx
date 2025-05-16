import {
  createRootRoute,
  Outlet,
  useLoaderData,
  useLocation,
  useNavigate,
} from "@tanstack/react-router";
import { userAtom } from "@/lib/atoms";
import { useSetAtom } from "jotai";
import { Toaster } from "@/components/ui/sonner";
import { useEffect } from "react";
export const Route = createRootRoute({
  loader: async () => {
    try {
      const res = await fetch("/api/authenticate", {
        // Add a short timeout to prevent long loading times if server is down
        signal: AbortSignal.timeout(5000),
        // Add cache control to prevent caching of authentication status
        headers: {
          "Cache-Control": "no-cache",
          Pragma: "no-cache",
        },
      });

      if (!res.ok) {
        console.log("Authentication failed with status:", res.status);
        return { error: "user is not authenticated", status: res.status };
      }

      const data = await res.json();
      return data;
    } catch (error) {
      console.error("Authentication error:", error);
      // Return a default error response that won't break the app
      return {
        error: "user is not authenticated",
        networkError: true,
        errorMessage: error instanceof Error ? error.message : String(error),
      };
    }
  },
  component: function Component() {
    const data = useLoaderData({ from: "__root__" });
    const setAtom = useSetAtom(userAtom);
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
      console.log("Authentication data:", data);

      if (data.error && data.error === "user is not authenticated") {
        if (
          location.pathname === "/" ||
          location.pathname.startsWith("/_protected") ||
          location.pathname === "/application"
        ) {
          navigate({
            to: "/login",
          });
        }
      } else {
        setAtom(data);
      }
    }, [data, location.pathname, navigate, setAtom]);

    return (
      <>
        <Outlet />
        <Toaster />
      </>
    );
  },
});
