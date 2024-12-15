import React from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Input } from "@/components/Input";
import { FormProvider, useForm } from "react-hook-form";
import { SignupSchema, SignUpType } from "@/lib/schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Link } from "@tanstack/react-router";
import SelectFormControl from "@/components/select";
import { SignupDepartments } from "@/contants";
import { toast } from "sonner";
const SignUpForm = () => {
  const [pending, setPending] = React.useState(false);
  const form = useForm<SignUpType>({
    resolver: zodResolver(SignupSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      department: "",
    },
  });
  const onSubmit = async (values: SignUpType) => {
    setPending(true);
    const res = await fetch("/api/auth/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(values),
    });
    if (res.status !== 200) {
      toast.error("Failed to create account");
      return;
    }
    toast.success("Account created successfully verify your account");
    setPending(false);
  };
  return (
    <Card className="w-[90%] md:w-[50%] lg:w-[40%] m-auto">
      <CardHeader>
        <h1 className="text-3xl font-bold m-auto">SignUp</h1>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form
            className="w-full space-y-4"
            onSubmit={form.handleSubmit(onSubmit)}
          >
            <FormProvider {...form}>
              <Input label="Email" name="email" />
              <Input label="Username" name="name" />
              <Input label="Password" name="password" type="password" />
              <SelectFormControl
                options={SignupDepartments}
                placeholder="Select a department"
                name="department"
                label="Department"
              />
            </FormProvider>
            <Button
              className="bg-[#d17a00] w-full text-white text-[16px]"
              disabled={pending}
            >
              {pending ? "pending..." : "Signup"}
            </Button>
          </form>
        </Form>
      </CardContent>
      <CardFooter className="flex flex-col gap-3 w-full">
        <Link
          className="border-[#d17a00] border-2  hover:border-[#d17a00]  text-black text-[16px] rounded-lg py-1 text-center w-full"
          to="/login"
          // disabled={isExecuting}
        >
          SignIn
        </Link>
      </CardFooter>
    </Card>
  );
};

export default SignUpForm;
