import {
  myApplicationsAtom,
  userAtom,
  turn_in_applicationAtom,
} from "@/lib/atoms";
import {
  createFileRoute,
  useLoaderData,
  useNavigate,
} from "@tanstack/react-router";
import { useAtom, useSetAtom, useAtomValue } from "jotai";
import { useEffect } from "react";
import { toast } from "sonner";
import { Card, CardContent, CardTitle, CardHeader } from "@/components/ui/card";
import { CheckCircle, Clock, XCircle } from "lucide-react";
export type DocumentRecord = {
  created_at: string; // ISO timestamp (e.g., "2024-12-15T11:37:29")
  created_by_id: string; // UUID of the user who created the record
  current_handler_id: string; // UUID of the current handler
  description: string; // A description of the record
  document_url: string; // URL to the document
  id: string; // UUID of the record
  status: "forwarded" | "pending" | "accepted" | "rejected"; // Status (use union type if statuses are predefined)
};
import { Badge } from "@/components/ui/badge";
export const Route = createFileRoute("/_protected/")({
  loader: async () => {
    const res = await fetch("/api/application/all", {
      method: "POST",
    });
    if (res.status !== 200) {
      toast.error("Failed to load application");
    }
    return (await res.json()).applications;
  },
  component: RouteComponent,
});
export const getStatusColor = (status: DocumentRecord["status"]) => {
  switch (status) {
    case "accepted":
      return "bg-green-100 text-green-800";
    case "pending":
      return "bg-yellow-100 text-yellow-800";
    case "rejected":
      return "bg-red-100 text-red-800";
  }
};
export const getStatusIcon = (status: DocumentRecord["status"]) => {
  switch (status) {
    case "accepted":
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    case "pending":
      return <Clock className="h-5 w-5 text-yellow-500" />;
    case "rejected":
      return <XCircle className="h-5 w-5 text-red-500" />;
  }
};

function RouteComponent() {
  const data = useLoaderData({ from: "/_protected/" });
  const userData = useAtomValue(userAtom);
  const [myapplications, setMyApplications] = useAtom(myApplicationsAtom);
  const setTurnInApplications = useSetAtom(turn_in_applicationAtom);
  const navigate = useNavigate();
  useEffect(() => {
    const myApplications =
      data.length > 0
        ? data?.filter(
            (document: DocumentRecord) =>
              document.created_by_id === userData?.id
          )
        : null;
    const turnInApplications =
      data.length > 0
        ? data.filter(
            (document: DocumentRecord) =>
              document.current_handler_id === userData?.id
          )
        : null;
    setMyApplications(myApplications);
    setTurnInApplications(turnInApplications);
  }, [data, userData]);
  console.log(myapplications);
  const acceptedCount = myapplications?.reduce(
    (acc, curr) => (curr.status === "accepted" ? acc + 1 : acc),
    0
  );
  const pendingCount = myapplications?.reduce(
    (acc, curr) => (curr.status === "pending" ? acc + 1 : acc),
    0
  );
  const rejectedCount = myapplications?.reduce(
    (acc, curr) => (curr.status === "rejected" ? acc + 1 : acc),
    0
  );

  return (
    <div className="w-[100dvw] lg:w-[80dvw]">
      <h1 className="text-xl font-bold text-center mb-3">My applications</h1>
      <div className="w-full px-4 flex flex-col md:flex-row justify-between gap-2">
        <Card className="flex flex-col justify-center items-center w-[90%]  md:w-1/4 text-green-500">
          <CardTitle className="text-center text-2xl font-bold">
            {" "}
            {acceptedCount}
          </CardTitle>
          <CardContent className="text-center text-xl">Accepted</CardContent>
        </Card>
        <Card className="flex flex-col justify-center items-center w-[90%]  md:w-1/4 text-yellow-500">
          <CardTitle className="text-center text-2xl font-bold">
            {pendingCount}
          </CardTitle>
          <CardContent className="text-center text-xl">Pending</CardContent>
        </Card>
        <Card className="flex flex-col justify-center items-center w-[90%] md:w-1/4 text-red-500">
          <CardTitle className="text-center text-2xl font-bold">
            {rejectedCount}
          </CardTitle>
          <CardContent className="text-center text-xl">Rejected</CardContent>
        </Card>
      </div>
      <div>
        <h1 className="text-xl font-bold text-center mb-3">Applications</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
          {myapplications?.map((application) => (
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
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
