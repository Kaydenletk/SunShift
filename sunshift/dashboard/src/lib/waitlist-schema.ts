import { z } from 'zod';

export const waitlistEntrySchema = z
  .object({ email: z.string().trim().email() })
  .transform((data) => ({ email: data.email.toLowerCase() }));

export type WaitlistEntryInput = z.input<typeof waitlistEntrySchema>;
export type WaitlistEntry = z.output<typeof waitlistEntrySchema>;
