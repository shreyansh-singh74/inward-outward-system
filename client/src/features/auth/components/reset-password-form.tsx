import React from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import { FormProvider, useForm } from "react-hook-form";
import { ResetPasswordType, ResetPasswordSchema } from "@/lib/schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/Input";
import { Button } from "@/components/ui/button";
import { useNavigate, useParams } from "@tanstack/react-router";
import { toast } from "sonner";
const ResetPasswordForm = () => {
  const form = useForm<ResetPasswordType>({
    resolver: zodResolver(ResetPasswordSchema),
    defaultValues: {
      newPassword: "",
      confirmPassword: "",
    },
  });
  const [loading, setLoading] = React.useState(false);
  const { token } = useParams({ from: "/_auth/reset-password/$token" });
  const navigate = useNavigate();
  const onSubmit = async (resetPasswordData: ResetPasswordType) => {
    setLoading(true);
    const res = await fetch(`/api/auth/password-reset-confirm/${token}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        new_password: resetPasswordData.newPassword,
        confirm_password: resetPasswordData.confirmPassword,
      }),
    });
    if (res.status !== 200) {
      toast.error("Failed to reset password");
      setLoading(false);
      return;
    }
    toast.success("Password reset successfully");
    navigate({ to: "/login" });
    setLoading(false);
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
