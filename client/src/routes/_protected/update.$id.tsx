import { createFileRoute } from "@tanstack/react-router";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import { FormProvider, useForm } from "react-hook-form";
import SelectFormControl from "@/components/select";
import { Input } from "@/components/Input";
import TextArea from "@/components/Textarea";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { useAtomValue } from "jotai";
import { currentApplication as atom } from "@/lib/atoms";
import { createApplicationSchema, createApplicationType } from "@/lib/schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { turn_in_receivers } from "@/contants";
import { objectToFormData } from "@/utils";
import { toast } from "sonner";
export const Route = createFileRoute("/_protected/update/$id")({
  component: RouteComponent,
});

function RouteComponent() {
  const [pending, setPending] = useState(false);
  const currentApplication = useAtomValue(atom);
  const form = useForm<createApplicationType>({
    resolver: zodResolver(createApplicationSchema),
    defaultValues: {
      description: "",
      for_user: "",
      subject: "",
    },
  });
  useEffect(() => {
    form.setValue("description", currentApplication?.description || "");
    form.setValue("for_user", currentApplication?.to || "");
    form.setValue("subject", currentApplication?.subject || "");
  });
  const onSubmit = async (values: createApplicationType) => {
    const formdata = objectToFormData(values);
    setPending(true);
    const res = await fetch(
      `/api/application/update_app/${currentApplication?.id}`,
      {
        method: "POST",
        body: formdata,
      }
    );
    if (res.status !== 200) {
      toast.error("Failed to update application");
    } else {
      toast.success("Application updated successfully");
    }
    setPending(false);
    form.reset();
  };
  return (
    <div>
      <div className="flex w-[80dvw] h-full flex-grow  justify-center items-center">
        <Card className="p-4 w-[99%] md:w-[50%] mx-auto">
          <CardTitle className="text-xl font-bold text-center">
            Update Application
          </CardTitle>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)}>
                <FormProvider {...form}>
                  <SelectFormControl
                    options={turn_in_receivers}
                    label="For"
                    name="for_user"
                    placeholder="Select whom you want to give this application"
                  />
                  <Input name="subject" label="Enter the subject" />
                  <TextArea
                    label="Description of query"
                    name="description"
                    placeholder="Enter the description of your query"
                  />
                  <Input type="file" name="document" label="Document" />
                  <Button
                    className="bg-[#d17a00] w-full mt-3"
                    disabled={pending}
                  >
                    {pending ? "Submitting..." : "Submit"}
                  </Button>
                </FormProvider>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
