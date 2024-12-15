import { z } from "zod";
export const SignupSchema = z.object({
  name: z.string().min(1, { message: "Username is required" }),
  department: z.string().optional(),
  email: z.string().email(),
  password: z
    .string()
    .min(8, { message: "Min length of password should be 8" }),
});
export const LoginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1, { message: "Password is required" }),
});

export type LoginType = z.infer<typeof LoginSchema>;
export type SignUpType = z.infer<typeof SignupSchema>;
