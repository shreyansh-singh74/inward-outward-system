import React from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import { FormProvider, useForm } from "react-hook-form";
import { ForgotPasswordSchema, ForgotPasswordType } from "@/lib/schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/Input";
import { Button } from "@/components/ui/button";

const ForgotPasswordForm = () => {
  const form = useForm<ForgotPasswordType>({
    resolver: zodResolver(ForgotPasswordSchema),
    defaultValues: {
      email: "",
    },
  });
  const [loading, setLoading] = React.useState(false);
  const onSubmit = async (ForgetPasswordData: ForgotPasswordType) => {
    setLoading(true);
    console.log(ForgetPasswordData);
    setLoading(false);
  };
  return (
    <div>
      <Card className="w-[90%] md:w-[50%] lg:w-[40%] mx-auto">
        <CardHeader>
          <h1 className="text-3xl font-bold m-auto">Forget Password</h1>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form
              className="w-full space-y-4"
              onSubmit={form.handleSubmit(onSubmit)}
            >
              <FormProvider {...form}>
                <Input label="Email" name="email" />
              </FormProvider>
              <Button
                type="submit"
                className="bg-[#d17a00] hover:bg-[#d17a00] dark:bg-blue-600 w-full text-white text-[16px] p-2 rounded-md"
                disabled={loading}
              >
                {loading ? "pending..." : "Submit"}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
};

export default ForgotPasswordForm;
