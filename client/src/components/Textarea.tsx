import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useFormContext } from "react-hook-form";
import { Textarea } from "./ui/textarea";
const TextArea = ({
  label,
  name,
  placeholder,
  maxLength,
}: {
  label: string;
  name: string;
  placeholder: string;
  maxLength?: number;
}) => {
  const { control } = useFormContext();
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel className="text-md font-semibold">{label}</FormLabel>
          <FormControl>
            <Textarea
              placeholder={placeholder}
              maxLength={maxLength}
              {...field}
            />
          </FormControl>
          {typeof maxLength === "number" && (
            <p className="text-xs text-muted-foreground text-right">
              {(field.value?.length || 0)}/{maxLength}
            </p>
          )}
          <FormMessage />
        </FormItem>
      )}
    />
  );
};

export default TextArea;
