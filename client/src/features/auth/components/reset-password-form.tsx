import React from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import { FormProvider, useForm } from "react-hook-form";
import { ResetPasswordType, ResetPasswordSchema } from "@/lib/schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/Input";
import { Button } from "@/components/ui/button";
const ResetPasswordForm = () => {
  const form = useForm<ResetPasswordType>({
    resolver: zodResolver(ResetPasswordSchema),
    defaultValues: {
      newPassword: "",
      confirmPassword: "",
    },
  });
  const [loading, setLoading] = React.useState(false);

  const onSubmit = async (resetPasswordData: ResetPasswordType) => {
    console.log(resetPasswordData);
  };
  return (
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
              <Input label="New Password" name="newPassword" type="password" />
              <Input
                label="Confirm Password"
                name="confirmPassword"
                type="password"
              />
            </FormProvider>
            <Button
              type="submit"
              className="bg-[#d17a00] w-full text-white text-[16px] p-2 rounded-md"
              disabled={loading}
            >
              {loading ? "pending..." : "Reset Password"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

export default ResetPasswordForm;
