"use client";

import { useState } from "react";
import { formatDate } from "@/features/users/component/table";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ChevronRight, ArrowRight, ArrowLeft, RefreshCw } from "lucide-react";
import { User } from "@/features/users/component/table";
// Helper function to get icon based on action type
function getActionIcon(actionType: string) {
  switch (actionType.toLowerCase()) {
    case "forward":
      return <ArrowRight className="h-6 w-6" />;
    case "backward":
      return <ArrowLeft className="h-6 w-6" />;
    case "review":
      return <RefreshCw className="h-6 w-6" />;
    default:
      return <ChevronRight className="h-6 w-6" />;
  }
}

interface Action {
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

interface ApplicationTimelineProps {
  application: {
    actions: Action[];
  };
}

export default function Actions({ application }: ApplicationTimelineProps) {
  const [selectedAction, setSelectedAction] = useState<Action | null>(null);
  const { actions } = application;
  const sortedAction = actions.sort(
    (a, b) => new Date(a.created_at) - new Date(b.created_at)
  );
  return (
    <section className="p-4">
      <h2 className="text-2xl font-semibold mb-6">Application Timeline</h2>

      <div className="relative">
        {/* Horizontal line */}
        <div className="absolute left-0 right-0 top-1/2 h-0.5 bg-gray-200 transform -translate-y-1/2"></div>

        {/* Timeline nodes */}
        <div className="flex flex-wrap justify-between relative z-10">
          {sortedAction.map((action, index) => (
            <Button
              key={action.id}
              variant="outline"
              className={`flex flex-col items-center p-2 bg-white hover:bg-gray-100 ${
                index === 0
                  ? "rounded-l-full"
                  : index === application.actions.length - 1
                    ? "rounded-r-full"
                    : ""
              }`}
              onClick={() => setSelectedAction(action)}
            >
              <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center mb-2">
                {getActionIcon(action.action_type)}
              </div>
              <span className="text-xs font-medium">{action.action_type}</span>
            </Button>
          ))}
        </div>
      </div>

      {/* Modal for detailed information */}
      <Dialog
        open={!!selectedAction}
        onOpenChange={() => setSelectedAction(null)}
      >
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Action Details</DialogTitle>
            <DialogDescription>
              {selectedAction &&
                `${selectedAction.action_type} - ${formatDate(selectedAction.created_at)}`}
            </DialogDescription>
          </DialogHeader>
          {selectedAction && (
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label className="text-right">From</Label>
                <Input
                  value={selectedAction.from_user.username}
                  readOnly
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label className="text-right">Role</Label>
                <Input
                  value={selectedAction.from_user.role}
                  readOnly
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label className="text-right">Department</Label>
                <Input
                  value={selectedAction.from_user.department}
                  readOnly
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label className="text-right">To</Label>
                <Input
                  value={selectedAction.to_user.username}
                  readOnly
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label className="text-right">Role</Label>
                <Input
                  value={selectedAction.to_user.role}
                  readOnly
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label className="text-right">Department</Label>
                <Input
                  value={selectedAction.to_user.department}
                  readOnly
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label className="text-right">Comments</Label>
                <Textarea
                  value={selectedAction.comments || "No comments"}
                  readOnly
                  className="col-span-3"
                />
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </section>
  );
}
