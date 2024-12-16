import { Button } from "@/components/ui/button";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import { User } from "@/features/users/component/table";
import { usersAtom } from "@/lib/atoms";
import {
  createFileRoute,
  useNavigate,
  useParams,
} from "@tanstack/react-router";
import { useAtomValue } from "jotai";
import { useForm, useWatch } from "react-hook-form";
import { UpdateUserSchema, UpdateUserType } from "@/lib/schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form } from "@/components/ui/form";
import SelectFormControl from "@/components/select";
import { role_and_departments } from "@/contants";
import { useEffect, useState } from "react";
import { toast } from "sonner";
export const Route = createFileRoute("/_protected/user/$id")({
  component: RouteComponent,
});

function RouteComponent() {
  const users = useAtomValue(usersAtom);
  const [department, setDepartment] = useState(role_and_departments.HOD);
  const navigate = useNavigate();
  const form = useForm<UpdateUserType>({
    resolver: zodResolver(UpdateUserSchema),
    defaultValues: {
      role: "HOD",
      department: "",
    },
  });
  const { id } = useParams({ from: "/_protected/user/$id" });
  const role = useWatch({
    control: form.control,
    name: "role",
  });
  useEffect(() => {
    //@ts-expect-error: Unreachable code error
    setDepartment(role_and_departments[role]);
  }, [role]);
  if (!users) {
    navigate({ to: "/" });
    return;
  }
  const onSubmit = async (values: UpdateUserType) => {
    const res = await fetch(`/api/sys_admin/update_user`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: id,
        role: values.role,
        department: values.department,
      }),
    });
    if (res.status !== 201) {
      toast.error("Some error taken place");
      return;
    }
    toast.success("User info updated successfully");
  };
  const currentUser = users.filter((user: User) => user.id === id)[0];
  return (
    <div className="flex w-[80dvw] h-full flex-grow  justify-center items-center">
      <Card className="p-4 w-[90%] md:w-[50%] mx-auto">
        <CardTitle className="text-xl font-bold text-center">
          Update User Info
        </CardTitle>
        <CardContent>
          <div className="flex justify-between my-3">
            <h1>
              <strong>Username:</strong>
              {currentUser?.username}
            </h1>
            <h1>
              <strong>Email:</strong>
              {currentUser?.tcet_email}
            </h1>
          </div>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
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
              <Button className="bg-[#d17a00] w-full mt-3">Submit</Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
