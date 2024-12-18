import {
  createFileRoute,
  useLoaderData,
  useNavigate,
  useParams,
} from "@tanstack/react-router";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { formatDate } from "@/features/users/component/table";
import { useAtomValue } from "jotai";
import { userAtom } from "@/lib/atoms";
import { AcceptDialog } from "@/components/AcceptDialog";
import { RejectDialog } from "@/components/RejectDialog";
import { ExternalLink } from "lucide-react";
interface User {
  id: string;
  name: string;
  role: string;
  department: string;
  tcet_email: string;
  created_at: string;
  isEmailVerified: boolean;
}

interface ApplicationAction {
  action_type: string;
  application_id: string;
  comments: string | null;
  created_at: string;
  from_user: User;
  from_user_id: string;
  id: string;
  to_user: User;
  to_user_id: string;
}

interface Application {
  id: string;
  created_at: string;
  created_by_id: string;
  created_by: User;
  current_handler_id: string;
  description: string;
  document: string | null;
  status: string;
  actions: ApplicationAction[];
  accept_reference_number?: string;
}

interface ApplicationDetailsProps {
  application: Application;
}

export const Route = createFileRoute("/_protected/application/$id")({
  component: RouteComponent,
  loader: async ({ params }) => {
    const res = await fetch(`/api/application/${params.id}`, {
      method: "GET",
    });
    if (res.status != 200) {
      toast.error("Failed to load application");
      // router.navigate({ to: "/" });
    }
    return await res.json();
  },
});

function RouteComponent() {
  const data = useLoaderData({ from: "/_protected/application/$id" });
  const user = useAtomValue(userAtom);
  const { id } = useParams({ from: "/_protected/application/$id" });
  const navigate = useNavigate();
  if (!user) return;
  if (!data) return <div>Loading...</div>;
  if (!data.application) {
    navigate({ to: "/" });
    return;
  }
  const { application } = data as ApplicationDetailsProps;
  console.log(application);
  const document_name = application.document?.split("/")[1];
  const handleClick = () => {
    const url = `http://localhost:5173/api/documents/${document_name}`;
    window.open(url, "_blank");
  };

  return (
    <div className="w-[100dvw] lg:w-[80dvw]">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Application Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Application Information */}
          <section className="space-y-2">
            <h2 className="text-xl font-semibold">Application Information</h2>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div>
                <Label>Status</Label>
                <Input value={application.status} readOnly />
              </div>
              <div>
                <Label>Created At</Label>
                <Input value={formatDate(application.created_at)} readOnly />
              </div>
              <div>
                <Label>Document URL</Label>
                <div className="flex items-center gap-1">
                  <Input value={document_name || "No document"} readOnly />
                  <Button
                    variant={"secondary"}
                    className="bg-[#d17a00] text-white hover:bg-[#d17a00]"
                    onClick={handleClick}
                  >
                    <ExternalLink />
                  </Button>
                </div>
              </div>
            </div>
            <div>
              <Label>Description</Label>
              <Textarea value={application.description} readOnly />
            </div>
          </section>

          {/* Created By User Information */}
          <section className="space-y-2">
            <h2 className="text-xl font-semibold">Created By</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div>
                <Label>Username</Label>
                <Input
                  value={
                    // @ts-expect-error: Unreachable code error
                    application.created_by.username
                  }
                  readOnly
                />
              </div>
              <div>
                <Label>Role</Label>
                <Input value={application.created_by.role} readOnly />
              </div>
              <div>
                <Label>Department</Label>
                <Input value={application.created_by.department} readOnly />
              </div>
              <div>
                <Label>Email</Label>
                <Input value={application.created_by.tcet_email} readOnly />
              </div>
              {application.accept_reference_number && (
                <div>
                  <Label>Reference Number</Label>
                  <Input value={application.accept_reference_number} readOnly />
                </div>
              )}
            </div>
          </section>

          {/* Application Actions */}
          <section className="space-y-2">
            <h2 className="text-xl font-semibold">Application Actions</h2>
            {application.actions.map((action, index) => (
              <Card key={action.id} className="p-4">
                <h3 className="font-semibold mb-2">Action {index + 1}</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Action Type</Label>
                    <Input value={action.action_type} readOnly />
                  </div>
                  <div>
                    <Label>Created At</Label>
                    <Input value={formatDate(action.created_at)} readOnly />
                  </div>
                  <div className="flex gap-3 flex-col">
                    <Label>From User</Label>
                    <Input
                      value={
                        // @ts-expect-error: Unreachable code error
                        action.from_user.username
                      }
                      readOnly
                    />
                    <Input value={action.from_user.role} readOnly />
                    <Input value={action.from_user.department} readOnly />
                  </div>
                  <div className="flex gap-3 flex-col">
                    <Label>To User</Label>
                    <Input value={action.to_user.name} readOnly />
                    <Input value={action.to_user.role} readOnly />
                    <Input value={action.to_user.department} readOnly />
                  </div>
                </div>
                <div className="mt-2">
                  <Label>Comments</Label>
                  <Textarea
                    value={
                      // @ts-expect-error: Unreachable code error
                      action.comment || "No comments"
                    }
                    readOnly
                  />
                </div>
              </Card>
            ))}
          </section>

          {/* New Action */}
        </CardContent>

        {/* Action Buttons */}
        {application.current_handler_id === user?.id && (
          <CardFooter className="flex justify-between flex-col md:flex-row gap-4">
            <AcceptDialog id={id}>
              <Button className="bg-green-500 hover:bg-green-600 w-full md:w-[33%]">
                Accept
              </Button>
            </AcceptDialog>
            <RejectDialog id={id}>
              <Button className="bg-red-500 hover:bg-red-600 w-full md:w-[33%]">
                Reject
              </Button>
            </RejectDialog>
            <Button
              className="bg-blue-500 hover:bg-blue-600 w-full md:w-[33%]"
              onClick={() => navigate({ to: `/forward/${application.id}` })}
            >
              Forward
            </Button>
          </CardFooter>
        )}
      </Card>
    </div>
  );
}
