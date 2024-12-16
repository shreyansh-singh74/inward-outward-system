import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useAtomValue } from "jotai";
import { turn_in_applicationAtom } from "@/lib/atoms";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { DocumentRecord } from ".";
import { getStatusColor, getStatusIcon } from "./index";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/features/users/component/table";
export const Route = createFileRoute("/_protected/hand_in")({
  component: RouteComponent,
});

function RouteComponent() {
  const turnInApplications = useAtomValue(turn_in_applicationAtom);
  const navigate = useNavigate();
  return (
    <div className="w-[100dvw] lg:w-[80dvw]">
      <h1 className="text-xl font-bold text-center mb-3">
        Handed applications
      </h1>
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
