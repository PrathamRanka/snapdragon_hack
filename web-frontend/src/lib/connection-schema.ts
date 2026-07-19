import { z } from "zod";

export const connectionSchema = z.object({
  backendUrl: z
    .url("Enter a valid backend URL")
    .refine((value) => value.startsWith("http://") || value.startsWith("https://"), {
      message: "Use an http:// or https:// backend URL",
    }),
  sessionId: z.string().trim().min(1, "Session ID is required").max(128),
  token: z.string().trim().min(20, "Enter the signed dashboard token"),
});

export type ConnectionFormValues = z.infer<typeof connectionSchema>;

