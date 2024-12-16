import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { useState } from "react";
export function RejectDialog({
  children,
  id,
}: {
  children: React.ReactNode;
  id: string;
}) {
  const [input, setInput] = useState("");
  const onClick = async () => {
    const res = await fetch(`/api/application/update/${id}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status: "REJECTED",
        remark: input,
      }),
    });
    if (res.status !== 200) {
      toast.error("Failed to accept application");
    } else {
      toast.success("Application rejected successfully");
    }
  };
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>{children}</AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
          <AlertDialogDescription>
            <Label>Reason</Label>
            <Input value={input} onChange={(e) => setInput(e.target.value)} />
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={onClick}>Continue</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
