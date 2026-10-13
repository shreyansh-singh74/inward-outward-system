import React from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Input } from "@/components/Input";
import { FormProvider, useForm, useWatch } from "react-hook-form";
import {
  OTPVerificationSchema,
  OTPVerificationType,
  SignupSchema,
  SignUpType,
} from "@/lib/schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Link, useNavigate, useRouter } from "@tanstack/react-router";
import SelectFormControl from "@/components/select";
import {
  SignupDepartments,
  DeanPortfolios,
  DeanPortfolioLabels,
  TeacherDesignations,
} from "@/contants";
import { toast } from "sonner";

const SignUpForm = () => {
  const navigate = useNavigate();
  const router = useRouter();
  const [pending, setPending] = React.useState(false);
  const [otpSent, setOtpSent] = React.useState(false);
  const [signupData, setSignupData] = React.useState<SignUpType | null>(null);
  const [apiError, setApiError] = React.useState<string | null>(null);

  // Signup form
  const signupForm = useForm<SignUpType>({
    resolver: zodResolver(SignupSchema),
    defaultValues: {
      name: "",
      email: "",
      userType: "student",
      designation: "",
      department: "",
    },
  });

  const userType = useWatch({
    control: signupForm.control,
    name: "userType",
  });

  const designation = useWatch({
    control: signupForm.control,
    name: "designation",
  });

  // Automatically assign department for Principal and Vice Principal,
  // and clear stale department when designation changes (prevents blank dropdown)
  React.useEffect(() => {
    if (userType === "teacher") {
      if (designation === "Principal") {
        signupForm.setValue("department", "PRINCIPAL", {
          shouldValidate: true,
        });
      } else if (designation === "Vice Principal") {
        signupForm.setValue("department", "VICE_PRINCIPAL", {
          shouldValidate: true,
        });
      } else if (
        designation === "Dean" ||
        designation === "Associate Dean"
      ) {
        const current = signupForm.getValues("department");
        if (current && !DeanPortfolios.includes(current)) {
          signupForm.setValue("department", "", { shouldValidate: true });
        }
      } else if (
        designation === "HOD" ||
        designation === "Associate HOD" ||
        designation === "Faculty"
      ) {
        const current = signupForm.getValues("department");
        if (current && !SignupDepartments.includes(current)) {
          signupForm.setValue("department", "", { shouldValidate: true });
        }
      }
    }
  }, [designation, userType, signupForm]);

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
    setPending(true);
    setApiError(null);

    let role = "student";
    let department = values.department || "";

    if (values.userType === "teacher") {
      switch (values.designation) {
        case "Principal":
          role = "principal";
          department = "PRINCIPAL";
          break;
        case "Vice Principal":
          role = "vice_principal";
          department = "VICE_PRINCIPAL";
          break;
        case "Dean":
          role = "dean";
          break;
        case "Associate Dean":
          role = "associate_dean";
          break;
        case "HOD":
          role = "hod";
          break;
        case "Associate HOD":
          role = "associate_hod";
          break;
        case "Faculty":
          role = "faculty";
          break;
        default:
          role = "faculty";
      }
    }

    const payload = {
      name: values.name,
      email: values.email,
      role: role,
      department: department,
    };

    try {
      const res = await fetch("/api/auth/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const responseData = await res.json();

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

      if (!res.ok) {
        setApiError(data.message || "Invalid OTP");
        toast.error(data.message || "Invalid OTP");
        setPending(false);
        return;
      }

      toast.success("Account created successfully");
      // Navigate to home/dashboard after successful signup
      await router.invalidate();
      await navigate({ to: "/" });
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
    setOtpSent(false);
    setSignupData(null);
    setApiError(null);
    otpForm.reset(); // Reset OTP form completely
  };

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

                {/* Filter for Student or Teacher */}
                <div className="space-y-2">
                  <label className="text-md font-semibold">I am a</label>
                  <div className="grid grid-cols-2 gap-2">
                    <Button
                      type="button"
                      variant={userType === "student" ? "default" : "outline"}
                      className={
                        userType === "student"
                          ? "bg-[#d17a00] hover:bg-[#a05e00] text-white"
                          : "hover:bg-muted"
                      }
                      onClick={() => {
                        signupForm.setValue("userType", "student", {
                          shouldValidate: true,
                        });
                        signupForm.setValue("designation", "");
                        signupForm.setValue("department", "");
                      }}
                    >
                      Student
                    </Button>
                    <Button
                      type="button"
                      variant={userType === "teacher" ? "default" : "outline"}
                      className={
                        userType === "teacher"
                          ? "bg-[#d17a00] hover:bg-[#a05e00] text-white"
                          : "hover:bg-muted"
                      }
                      onClick={() => {
                        signupForm.setValue("userType", "teacher", {
                          shouldValidate: true,
                        });
                        signupForm.setValue("designation", "");
                        signupForm.setValue("department", "");
                      }}
                    >
                      Teacher
                    </Button>
                  </div>
                </div>

                {/* Student: Choose Department */}
                {userType === "student" && (
                  <SelectFormControl
                    options={SignupDepartments}
                    placeholder="Select a department"
                    name="department"
                    label="Department"
                  />
                )}

                {/* Teacher: Designation and Portfolio/Department Selection */}
                {userType === "teacher" && (
                  <>
                    <SelectFormControl
                      options={[...TeacherDesignations]}
                      placeholder="Select teacher designation"
                      name="designation"
                      label="Designation"
                    />

                    {/* Dean portfolios */}
                    {designation === "Dean" && (
                      <SelectFormControl
                        options={DeanPortfolios}
                        getLabel={(v) => DeanPortfolioLabels[v] ?? v}
                        placeholder="Select Dean portfolio"
                        name="department"
                        label="Dean Portfolio"
                      />
                    )}

                    {/* Associate Dean portfolios */}
                    {designation === "Associate Dean" && (
                      <SelectFormControl
                        options={DeanPortfolios}
                        getLabel={(v) => DeanPortfolioLabels[v] ?? v}
                        placeholder="Select Associate Dean portfolio"
                        name="department"
                        label="Associate Dean Portfolio"
                      />
                    )}

                    {/* HOD departments */}
                    {designation === "HOD" && (
                      <SelectFormControl
                        options={SignupDepartments}
                        placeholder="Select HOD department"
                        name="department"
                        label="Department"
                      />
                    )}

                    {/* Associate HOD departments */}
                    {designation === "Associate HOD" && (
                      <SelectFormControl
                        options={SignupDepartments}
                        placeholder="Select Associate HOD department"
                        name="department"
                        label="Department"
                      />
                    )}

                    {/* Faculty departments */}
                    {designation === "Faculty" && (
                      <SelectFormControl
                        options={SignupDepartments}
                        placeholder="Select Faculty department"
                        name="department"
                        label="Department"
                      />
                    )}

                    {/* Principal / Vice Principal confirmation */}
                    {(designation === "Principal" ||
                      designation === "Vice Principal") && (
                      <div className="p-3 text-sm rounded-md bg-amber-50 dark:bg-amber-950/30 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-900">
                        Designation {designation} selected.
                      </div>
                    )}
                  </>
                )}
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
          className="border-[#d17a00] border-2 hover:border-[#d17a00] text-black text-[16px] rounded-lg py-1 text-center w-full"
          to="/login"
        >
          Sign-in
        </Link>
      </CardFooter>
    </Card>
  );
};

export default SignUpForm;
