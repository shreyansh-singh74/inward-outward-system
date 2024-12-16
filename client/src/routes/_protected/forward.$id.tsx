import {
  createFileRoute,
  useNavigate,
  useParams,
} from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { forwardApplicationSchema, forwardApplicationType } from "@/lib/schema";
import { FormProvider, useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form } from "@/components/ui/form";
import SelectFormControl from "@/components/select";
import TextArea from "@/components/Textarea";
import { useState, useEffect } from "react";
import { role_and_departments } from "@/contants";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
export const Route = createFileRoute("/_protected/forward/$id")({
  component: RouteComponent,
});

function RouteComponent() {
  const [department, setDepartment] = useState([]);
  const [pending, setPending] = useState(false);
  const navigate = useNavigate();
  const form = useForm<forwardApplicationType>({
    resolver: zodResolver(forwardApplicationSchema),
    defaultValues: {
      role: "HOD",
      department: "",
      remark: "",
    },
  });
  const role = useWatch({
    control: form.control,
    name: "role",
  });
  useEffect(() => {
    setDepartment(role_and_departments[role]);
  }, [role]);
  const { id } = useParams({ from: "/_protected/forward/$id" });
  const onSubmit = async (values: forwardApplicationType) => {
    setPending(true);
    const res = await fetch(`/api/application/forward/${id}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(values),
    });
    if (res.status !== 200) {
      toast.error("Failed to forward application");
    } else {
      toast.success("Application Forwarded successfully");
    }
    setPending(false);
    navigate({ to: "/" });
    form.reset();
  };
  return (
    <div className="w-[100dvw] lg:w-[80dvw] h-[60dvh] flex justify-center items-center">
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="text-center text-2xl">
            Forward Document
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
              <FormProvider {...form}>
                <SelectFormControl
                  options={Object.keys(role_and_departments)}
                  label="Role"
                  name="role"
                  placeholder="Select a Role for this user"
                />
                <SelectFormControl
                  label="Department"
                  name="department"
                  placeholder="Select a department"
                  options={department}
                />
                <TextArea
                  label="Remark"
                  name="remark"
                  placeholder="Enter the remark"
                />
                <Button className="bg-[#d17a00] w-full mt-3" disabled={pending}>
                  {pending ? "Submitting..." : "Submit"}
                </Button>
              </FormProvider>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
