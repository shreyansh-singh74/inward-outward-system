import {
  createFileRoute,
  useLoaderData,
  useNavigate,
} from "@tanstack/react-router";
import { toast } from "sonner";
import { UserTable } from "@/features/users/component/table";
import { useSetAtom } from "jotai";
import { usersAtom } from "@/lib/atoms";
import { useEffect } from "react";
export const Route = createFileRoute("/_protected/users")({
  loader: async () => {
    const res = await fetch(`/api/sys_admin/get_all_user`);
    if (res.status !== 200) {
      toast.error("Failed to fetch users");
    }
    const data = await res.json();
    if (!data.users) {
      return { error: "Failed to fetch user" };
    }
    return { users: data.users };
  },
  component: RouteComponent,
});

function RouteComponent() {
  const { users, error } = useLoaderData({ from: "/_protected/users" });
  const setAtom = useSetAtom(usersAtom);
  const navigate = useNavigate();
  useEffect(() => {
    if (error) {
      toast.error(error);
      navigate({ to: "/" });
    } else {
      setAtom(users);
    }
  }, [users, error]);

  return (
    <div>
      <h1 className="ml-3 text-2xl font-bold mb-5">All Application Users</h1>
      <div className="w-[90%] m-auto">
        <UserTable data={users} />
      </div>
    </div>
  );
}
