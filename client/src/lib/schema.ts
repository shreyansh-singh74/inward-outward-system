import { z } from "zod";
import { zfd } from "zod-form-data";

export const SignupSchema = z
  .object({
    name: z.string().min(1, { message: "Username is required" }),
    email: z.string().email({ message: "Invalid email address" }),
    userType: z.enum(["student", "teacher"], {
      required_error: "Please select whether you are a Student or Teacher",
    }),
    designation: z.string().optional(),
    department: z.string().optional(),
    role: z.string().optional(),
  })
  .superRefine((data, ctx) => {
    if (data.userType === "student") {
      if (!data.department || data.department.trim() === "") {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["department"],
          message: "Please select a department",
        });
      }
    } else if (data.userType === "teacher") {
      if (!data.designation || data.designation.trim() === "") {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["designation"],
          message: "Please select a designation",
        });
      } else if (
        data.designation !== "Principal" &&
        data.designation !== "Vice Principal" &&
        (!data.department || data.department.trim() === "")
      ) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["department"],
          message: "Please select a department or portfolio",
        });
      }
    }
  });

export const LoginSchema = z.object({
  email: z.string().email(),
});

export const OTPVerificationSchema = z.object({
  email: z.string().email(),
  otp: z.string().length(6, { message: "OTP must be 6 digits" }),
});

export const UpdateUserSchema = z.object({
  role: z.string(),
  department: z.string(),
});

const ALLOWED_UPLOAD_EXTENSIONS = ["pdf", "jpg", "jpeg", "png", "doc", "docx"];
const MAX_UPLOAD_SIZE_MB = 5;

export const createApplicationSchema = zfd.formData({
  description: z
    .string()
    .min(1, { message: "Description is required" })
    .max(256, { message: "Description must be 256 characters or less" }),
  for_user: z
    .string()
    .min(1, { message: "For user is required" })
    .max(200, { message: "Receiver must be 200 characters or less" }),
  subject: z
    .string()
    .min(1, { message: "Subject is required" })
    .max(200, { message: "Subject must be 200 characters or less" }),
  document: zfd
    .file()
    .refine((file) => !file || file.size < 1024 * 1024 * MAX_UPLOAD_SIZE_MB, {
      message: `File must be less than ${MAX_UPLOAD_SIZE_MB} MB`,
    })
    .refine(
      (file) => {
        if (!file) return true;
        const parts = file.name.split(".");
        const ext = (parts.length > 1 ? (parts.pop() ?? "") : "").toLowerCase();
        return ALLOWED_UPLOAD_EXTENSIONS.includes(ext);
      },
      {
        message: "Only PDF, JPG, JPEG, PNG, DOC, DOCX files are allowed",
      }
    )
    .optional(),
});

export const forwardApplicationSchema = z.object({
  role: z.string(),
  department: z.string(),
  remark: z.string().min(1, { message: "Remarks is required" }),
});

export type LoginType = z.infer<typeof LoginSchema>;
export type SignUpType = z.infer<typeof SignupSchema>;
export type OTPVerificationType = z.infer<typeof OTPVerificationSchema>;
export type UpdateUserType = z.infer<typeof UpdateUserSchema>;
export type createApplicationType = z.infer<typeof createApplicationSchema>;
export type forwardApplicationType = z.infer<typeof forwardApplicationSchema>;
