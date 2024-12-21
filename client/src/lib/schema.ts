import { z } from "zod";
import { zfd } from "zod-form-data";
export const SignupSchema = z.object({
  name: z.string().min(1, { message: "Username is required" }),
  department: z.string().optional(),
  email: z.string().email(),
});
export const LoginSchema = z.object({
  email: z.string().email(),
});
export const UpdateUserSchema = z.object({
  role: z.string(),
  department: z.string(),
});
export const createApplicationSchema = zfd.formData({
  description: z.string().min(1, { message: "Description is required" }),
  for_user: z.string().min(1, { message: "For user is required" }),
  subject: z.string().min(1, { message: "Supervisor is required" }),
  document: zfd
    .file()
    .refine((file) => file.size < 1024 * 1024 * 2, {
      message: "File must be less than 2 MB",
    })
    .optional(),
});
export const forwardApplicationSchema = z.object({
  role: z.string(),
  department: z.string(),
  remark: z.string().min(1, { message: "Remarks is required" }),
});
export type LoginType = z.infer<typeof LoginSchema>;
export type SignUpType = z.infer<typeof SignupSchema>;
export type UpdateUserType = z.infer<typeof UpdateUserSchema>;
export type createApplicationType = z.infer<typeof createApplicationSchema>;
export type forwardApplicationType = z.infer<typeof forwardApplicationSchema>;
