import { createFileRoute } from "@tanstack/react-router";
import { createApplicationSchema, createApplicationType } from "@/lib/schema";
import { FormProvider, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import SelectFormControl from "@/components/select";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/Input";
import TextArea from "@/components/Textarea";
import { objectToFormData } from "@/utils";
import { toast } from "sonner";
import { turn_in_receivers } from "@/contants";
export const Route = createFileRoute("/_protected/turn_in")({
  component: RouteComponent,
});

function RouteComponent() {
  const [pending, setPending] = useState(false);
  const form = useForm<createApplicationType>({
    resolver: zodResolver(createApplicationSchema),
    defaultValues: {
      description: "",
      for_user: "",
      subject: "",
    },
  });
  const onSubmit = async (values: createApplicationType) => {
    const formdata = objectToFormData(values);
    setPending(true);
    const res = await fetch(`/api/application/create`, {
      method: "POST",
      body: formdata,
    });
    if (res.status !== 200) {
      toast.error("Failed to create application");
    } else {
      toast.success("Application created successfully");
    }
    setPending(false);
    form.reset();
  };
  return (
    <div className="flex w-[80dvw] h-full flex-grow  justify-center items-center">
      <Card className="p-4 w-[99%] md:w-[50%] mx-auto">
        <CardTitle className="text-xl font-bold text-center">
          Insert Application
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
