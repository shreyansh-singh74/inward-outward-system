import { createFileRoute } from "@tanstack/react-router";
import { useAtomValue } from "jotai";
import { userAtom } from "@/lib/atoms";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { CircleUserRound, ShieldCheck, Mail, Building2, User } from "lucide-react";

export const Route = createFileRoute("/_protected/profile")({
  component: RouteComponent,
});

function formatRole(role: string) {
  if (!role) return "—";
  return role
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function RouteComponent() {
  const user = useAtomValue(userAtom);

  if (!user) {
    return (
      <div className="w-[100dvw] lg:w-[80dvw] p-6">
        <p className="text-center text-gray-500">
          No user info available. Please log in again.
        </p>
      </div>
    );
  }

  const displayName = user.username || user.name || "—";

  return (
    <div className="w-[100dvw] lg:w-[80dvw] p-6 max-w-2xl mx-auto">
      <h1 className="text-xl font-bold text-center mb-6">Profile</h1>
      <Card>
        <CardHeader className="flex flex-row items-center gap-4">
          <div className="rounded-full bg-orange-100 p-3">
            <CircleUserRound className="h-10 w-10 text-[#d17a00]" />
          </div>
          <div>
            <CardTitle className="text-2xl">{displayName}</CardTitle>
            <Badge className="mt-2 bg-orange-100 text-orange-800 hover:bg-orange-100">
              <ShieldCheck className="h-3 w-3 mr-1" />
              {formatRole(user.role)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Separator />
          <div className="flex items-center gap-3">
            <User className="h-4 w-4 text-gray-500" />
            <div>
              <p className="text-xs text-gray-500">Name</p>
              <p className="font-medium">{displayName}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Mail className="h-4 w-4 text-gray-500" />
            <div>
              <p className="text-xs text-gray-500">Email</p>
              <p className="font-medium break-all">{user.email || "—"}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <ShieldCheck className="h-4 w-4 text-gray-500" />
            <div>
              <p className="text-xs text-gray-500">Role</p>
              <p className="font-medium">{formatRole(user.role)}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Building2 className="h-4 w-4 text-gray-500" />
            <div>
              <p className="text-xs text-gray-500">Department</p>
              <p className="font-medium">{user.department || "—"}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
