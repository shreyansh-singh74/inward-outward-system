import { Input as ShadCnInput } from "./ui/input";
import {
  FormField,
  FormItem,
  FormControl,
  FormLabel,
  FormMessage,
} from "./ui/form";
import { useFormContext } from "react-hook-form";

export const Input = ({
  label,
  name,
  type = "text",
  placeholder,
  maxLength,
}: {
  label: string;
  name: string;
  type?: string;
  placeholder?: string;
  maxLength?: number;
}) => {
  const form = useFormContext();

  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel className="text-md font-semibold">{label}</FormLabel>
          <FormControl>
            {type === "file" ? (
              <ShadCnInput
                type="file"
                onChange={(e) => {
                  const file = e.target.files ? e.target.files[0] : null;
                  field.onChange(file); // Handle file input change
                }}
              />
            ) : (
              <ShadCnInput
                {...field}
                type={type}
                placeholder={placeholder || `Enter the ${label}`}
                maxLength={maxLength}
              />
            )}
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
};
