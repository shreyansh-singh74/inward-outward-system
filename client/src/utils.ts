export function objectToFormData(obj: Record<string, any>): FormData {
  const formData = new FormData();
  console.log(obj);
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const value = obj[key];
      if (value === undefined) {
        continue;
      }
      if (Array.isArray(value)) {
        value.forEach((item) => formData.append(key, item));
      } else if (value instanceof File) {
        formData.append(key, value, value.name);
      } else if (value instanceof Blob) {
        formData.append(key, value);
      } else if (typeof value === "object" && value !== null) {
        formData.append(key, JSON.stringify(value));
      } else {
        formData.append(key, String(value));
      }
    }
  }

  return formData;
}
