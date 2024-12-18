import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useAtomValue, useSetAtom } from "jotai";
import { turn_in_applicationAtom, userAtom } from "@/lib/atoms";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { DocumentRecord } from ".";
import { getStatusColor, getStatusIcon } from "./index";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/features/users/component/table";
import { toast } from "sonner";
import { useLoaderData } from "@tanstack/react-router";
import { useEffect } from "react";
import { useState } from "react";
import { Input } from "@/components/ui/input";
export const Route = createFileRoute("/_protected/hand_in")({
  component: RouteComponent,
  loader: async () => {
    const res = await fetch("/api/application/all", {
      method: "POST",
    });
    if (res.status !== 200) {
      toast.error("Failed to load application");
    }
    return (await res.json()).applications;
  },
});

function RouteComponent() {
  const turnInApplications = useAtomValue(turn_in_applicationAtom);
  const navigate = useNavigate();
  const data = useLoaderData({ from: "/_protected/hand_in" });
  const userData = useAtomValue(userAtom);
  const [searchQuery, setSearchQuery] = useState("");

  const setTurnInApplications = useSetAtom(turn_in_applicationAtom);
  useEffect(() => {
    let turnInApplications =
      data.length > 0
        ? data.filter(
            (document: DocumentRecord) =>
              document.current_handler_id === userData?.id
          )
        : null;
    if (searchQuery && turnInApplications) {
      console.log(turnInApplications);
      turnInApplications = turnInApplications.filter((item: DocumentRecord) =>
        item.accept_reference_number?.includes(searchQuery.toLowerCase())
      );
    }
    setTurnInApplications(turnInApplications);
  }, [data, userData, searchQuery]);
  console.log(turnInApplications);
  return (
    <div className="w-[100dvw] lg:w-[80dvw]">
      <h1 className="text-xl font-bold text-center mb-3">
        Handed applications
      </h1>
      <div className="w-[50dvw] mx-auto mb-6">
        <Input
          type="text"
          placeholder="Search by Reference Number..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full"
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
        {turnInApplications?.map((application: DocumentRecord) => (
          <Card
            key={application.id}
            className="w-full bg-white hover:bg-gray-50 transition-colors duration-200 ease-in-out border border-gray-200 shadow-sm hover:shadow-md"
            onClick={() => navigate({ to: `/application/${application.id}` })}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xl font-bold">
                {getStatusIcon(application.status)}
              </CardTitle>
              <Badge className={getStatusColor(application.status)}>
                {application.status}
              </Badge>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">{application.description}</p>
              <p className="text-gray-600">
                {formatDate(application.created_at)}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
