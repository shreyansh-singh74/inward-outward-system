"use client";
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
  LoginSchema,
  LoginType,
  OTPVerificationSchema,
  OTPVerificationType,
} from "@/lib/schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Link, useNavigate } from "@tanstack/react-router";
import { toast } from "sonner";

const SignInForm = () => {
  const navigate = useNavigate();
  const [otpSent, setOtpSent] = React.useState(false);
  const [userEmail, setUserEmail] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [apiError, setApiError] = React.useState<string | null>(null);

  // Debug state changes
  React.useEffect(() => {
    console.log("OTP sent state changed:", otpSent);
    console.log("User email:", userEmail);
  }, [otpSent, userEmail]);

  // Login form
  const loginForm = useForm<LoginType>({
    resolver: zodResolver(LoginSchema),
    defaultValues: {
      email: "",
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

  // Handler for login form submission (first step)
  const onSubmitEmail = async (values: LoginType) => {
    console.log("Submitting login form with values:", values);
    setLoading(true);
    setApiError(null);

    try {
      const res = await fetch(`/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(values),
      });

      console.log("Login API response status:", res.status);

      const responseData = await res.json();
      console.log("Login API response data:", responseData);

      if (!res.ok) {
        setApiError(responseData.message || "Failed to Login");
        toast.error(responseData.message || "Failed to Login");
        return;
      }

      // Save email for OTP verification
      setUserEmail(values.email);

      // Reset OTP form with email but empty OTP
      otpForm.reset({ email: values.email, otp: "" });

      // Show OTP screen
      setOtpSent(true);
      toast.success("OTP sent to your email");
    } catch (error) {
      console.error("Login API exception:", error);
      setApiError("Network error. Please try again.");
      toast.error("An error occurred");
    } finally {
      setLoading(false);
    }
  };

  // Handler for OTP verification form submission (second step)
  const onVerifyOTP = async (values: OTPVerificationType) => {
    console.log("Verifying OTP with values:", values);
    setLoading(true);
    setApiError(null);

    try {
      const res = await fetch(`/api/auth/verify-otp/login`, {
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
        return;
      }

      toast.success("Login successful");
      // Navigate to home/dashboard
      navigate({ to: "/" });
    } catch (error) {
      console.error("OTP verification API exception:", error);
      setApiError("Network error. Please try again.");
      toast.error("An error occurred");
    } finally {
      setLoading(false);
    }
  };

  // Handle resend OTP
  const handleResendOTP = async () => {
    if (!userEmail) return;
    console.log("Resending OTP for email:", userEmail);
    setLoading(true);
    setApiError(null);

    try {
      const res = await fetch(`/api/auth/resend-otp`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: userEmail }),
      });

      const data = await res.json();
      console.log("Resend OTP API response:", data);

      if (!res.ok) {
        setApiError(data.message || "Failed to resend OTP");
        toast.error("Failed to resend OTP");
        return;
      }

      toast.success("New OTP sent to your email");
    } catch (error) {
      console.error("Resend OTP API exception:", error);
      setApiError("Network error. Please try again.");
      toast.error("An error occurred");
    } finally {
      setLoading(false);
    }
  };

  // Go back to email input
  const handleBack = () => {
    console.log("Going back to email input");
    setOtpSent(false);
    setUserEmail("");
    setApiError(null);
    otpForm.reset(); // Reset OTP form completely
  };

  return (
    <Card className="w-[90%] md:w-[50%] lg:w-[40%] mx-auto">
      <CardHeader>
        <h1 className="text-3xl font-bold m-auto">Sign In</h1>
        {otpSent && (
          <p className="text-center text-sm text-gray-500">
            Enter the OTP sent to {userEmail}
          </p>
        )}
        {apiError && (
          <p className="text-center text-sm text-red-500 mt-2">{apiError}</p>
        )}
      </CardHeader>
      <CardContent>
        {!otpSent ? (
          // Email Input Form (First Step)
          <Form {...loginForm}>
            <form
              className="w-full space-y-4"
              onSubmit={loginForm.handleSubmit(onSubmitEmail)}
            >
              <FormProvider {...loginForm}>
                <Input label="Email" name="email" />
              </FormProvider>
              <Button
                className="bg-[#d17a00] w-full text-white text-[16px]"
                disabled={loading}
                type="submit"
              >
                {loading ? "Sending OTP..." : "Send OTP"}
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
                disabled={loading}
                type="submit"
              >
                {loading ? "Verifying..." : "Verify OTP"}
              </Button>
              <div className="flex justify-between text-sm">
                <button
                  type="button"
                  onClick={handleBack}
                  className="text-gray-500 hover:text-gray-700"
                >
                  Use different email
                </button>
                <button
                  type="button"
                  onClick={handleResendOTP}
                  className="text-[#d17a00] hover:text-[#a05e00]"
                  disabled={loading}
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
          to="/signup"
        >
          Sign-up
        </Link>
      </CardFooter>
    </Card>
  );
};

export default SignInForm;
