import React from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Input } from "@/components/Input";
import { FormProvider, useForm } from "react-hook-form";
import {
  OTPVerificationSchema,
  OTPVerificationType,
  SignupSchema,
  SignUpType,
} from "@/lib/schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Link, useNavigate } from "@tanstack/react-router";
import SelectFormControl from "@/components/select";
import { SignupDepartments } from "@/contants";
import { toast } from "sonner";

const SignUpForm = () => {
  console.log("Rendering SignUpForm component");
  const navigate = useNavigate();
  const [pending, setPending] = React.useState(false);
  const [otpSent, setOtpSent] = React.useState(false);
  const [signupData, setSignupData] = React.useState<SignUpType | null>(null);
  const [apiError, setApiError] = React.useState<string | null>(null);

  // Debug state changes
  React.useEffect(() => {
    console.log("OTP sent state changed:", otpSent);
    console.log("Signup data:", signupData);
  }, [otpSent, signupData]);

  // Signup form
  const signupForm = useForm<SignUpType>({
    resolver: zodResolver(SignupSchema),
    defaultValues: {
      name: "",
      email: "",
      department: "",
    },
  });

  // OTP verification form
  const otpForm = useForm<OTPVerificationType>({
    resolver: zodResolver(OTPVerificationSchema),
    defaultValues: {
      email: "",
      otp: "",
    },
  });

  // First step: send OTP
  const onSubmitSignup = async (values: SignUpType) => {
    console.log("Submitting signup form with values:", values);
    setPending(true);
    setApiError(null);

    try {
      const res = await fetch("/api/auth/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(values),
      });

      console.log("Signup API response status:", res.status);

      const responseData = await res.json();
      console.log("Signup API response data:", responseData);

      if (!res.ok) {
        console.error("Signup API error:", responseData);
        setApiError(responseData.message || "Failed to create account");
        toast.error(responseData.message || "Failed to create account");
        setPending(false);
        return;
      }

      // Store signup data and move to OTP verification
      setSignupData(values);

      // Reset OTP form with email but empty OTP
      otpForm.reset({ email: values.email, otp: "" });

      // Show OTP screen
      setOtpSent(true);
      toast.success("OTP sent to your email");
    } catch (error) {
      console.error("Signup API exception:", error);
      setApiError("Network error. Please try again.");
      toast.error("An error occurred");
    } finally {
      setPending(false);
    }
  };

  // Second step: verify OTP
  const onVerifyOTP = async (values: OTPVerificationType) => {
    console.log("Verifying OTP with values:", values);
    setPending(true);
    setApiError(null);

    try {
      const res = await fetch("/api/auth/verify-otp/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(values),
      });

      const data = await res.json();
      console.log("OTP verification API response:", data);

      if (!res.ok) {
        setApiError(data.message || "Invalid OTP");
        toast.error(data.message || "Invalid OTP");
        setPending(false);
        return;
      }

      toast.success("Account created successfully");
      // Navigate to home/dashboard after successful signup
      navigate({ to: "/" });
    } catch (error) {
      console.error("OTP verification API exception:", error);
      setApiError("Network error. Please try again.");
      toast.error("An error occurred");
    } finally {
      setPending(false);
    }
  };

  // Handle resend OTP
  const handleResendOTP = async () => {
    if (!signupData) return;
    console.log("Resending OTP for email:", signupData.email);
    setPending(true);
    setApiError(null);

    try {
      const res = await fetch("/api/auth/resend-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: signupData.email }),
      });

      const data = await res.json();
      console.log("Resend OTP API response:", data);

      if (!res.ok) {
        setApiError(data.message || "Failed to resend OTP");
        toast.error("Failed to resend OTP");
        setPending(false);
        return;
      }

      toast.success("New OTP sent to your email");
    } catch (error) {
      console.error("Resend OTP API exception:", error);
      setApiError("Network error. Please try again.");
      toast.error("An error occurred");
    } finally {
      setPending(false);
    }
  };

  // Go back to signup form
  const handleBack = () => {
    console.log("Going back to signup form");
    setOtpSent(false);
    setSignupData(null);
    setApiError(null);
    otpForm.reset(); // Reset OTP form completely
  };

  console.log("Current render state - OTP sent:", otpSent);

  return (
    <Card className="w-[90%] md:w-[50%] lg:w-[40%] m-auto">
      <CardHeader>
        <h1 className="text-3xl font-bold m-auto">SignUp</h1>
        {otpSent && signupData && (
          <p className="text-center text-sm text-gray-500">
            Enter the OTP sent to {signupData.email}
          </p>
        )}
        {apiError && (
          <p className="text-center text-sm text-red-500 mt-2">{apiError}</p>
        )}
      </CardHeader>
      <CardContent>
        {!otpSent ? (
          // Signup Form (First Step)
          <Form {...signupForm}>
            <form
              className="w-full space-y-4"
              onSubmit={signupForm.handleSubmit(onSubmitSignup)}
            >
              <FormProvider {...signupForm}>
                <Input label="Email" name="email" />
                <Input label="Username" name="name" />
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
                type="submit"
              >
                {pending ? "Sending OTP..." : "Send OTP"}
              </Button>
            </form>
          </Form>
        ) : (
          // OTP Verification Form (Second Step)
          <Form {...otpForm}>
            <form
              className="w-full space-y-4"
              onSubmit={otpForm.handleSubmit(onVerifyOTP)}
            >
              <FormProvider {...otpForm}>
                {/* Hidden field for email */}
                <input type="hidden" {...otpForm.register("email")} />

                {/* Use direct input instead of the Input component for OTP */}
                <div className="space-y-2">
                  <label className="text-md font-semibold">OTP</label>
                  <input
                    {...otpForm.register("otp")}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="Enter 6-digit OTP"
                    maxLength={6}
                    type="text"
                  />
                  {otpForm.formState.errors.otp && (
                    <p className="text-sm font-medium text-destructive">
                      {otpForm.formState.errors.otp.message}
                    </p>
                  )}
                </div>
              </FormProvider>
              <Button
                className="bg-[#d17a00] w-full text-white text-[16px]"
                disabled={pending}
                type="submit"
              >
                {pending ? "Verifying..." : "Verify OTP"}
              </Button>
              <div className="flex justify-between text-sm">
                <button
                  type="button"
                  onClick={handleBack}
                  className="text-gray-500 hover:text-gray-700"
                >
                  Change details
                </button>
                <button
                  type="button"
                  onClick={handleResendOTP}
                  className="text-[#d17a00] hover:text-[#a05e00]"
                  disabled={pending}
                >
                  Resend OTP
                </button>
              </div>
            </form>
          </Form>
        )}
      </CardContent>
      <CardFooter className="flex flex-col gap-2 w-full">
        <Link
          className="border-[#d17a00] border-2  hover:border-[#d17a00]  text-black text-[16px] rounded-lg py-1 text-center w-full"
          to="/login"
        >
          Sign-in
        </Link>
      </CardFooter>
    </Card>
  );
};

export default SignUpForm;
