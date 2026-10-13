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
  accept,
  hint,
}: {
  label: string;
  name: string;
  type?: string;
  placeholder?: string;
  maxLength?: number;
  accept?: string;
  hint?: string;
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
              <>
                <ShadCnInput
                  type="file"
                  accept={accept}
                  onChange={(e) => {
                    const file = e.target.files ? e.target.files[0] : null;
                    field.onChange(file); // Handle file input change
                  }}
                />
                {hint && (
                  <p className="text-xs text-muted-foreground mt-1">{hint}</p>
                )}
              </>
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
