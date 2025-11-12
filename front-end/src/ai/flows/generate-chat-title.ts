'use server';
/**
 * @fileOverview A flow to generate a concise title for a new chat session.
 *
 * - generateChatTitle - A function that creates a title from the user's first prompt.
 * - GenerateChatTitleInput - The input type for the generateChatTitle function.
 * - GenerateChatTitleOutput - The return type for the generateChatTitle function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const GenerateChatTitleInputSchema = z.object({
  prompt: z.string().describe('The initial user prompt for the chat session.'),
});
export type GenerateChatTitleInput = z.infer<typeof GenerateChatTitleInputSchema>;

const GenerateChatTitleOutputSchema = z.object({
    title: z.string().describe('A short, concise title (3-5 words) for the chat session.'),
});
export type GenerateChatTitleOutput = z.infer<typeof GenerateChatTitleOutputSchema>;

export async function generateChatTitle(input: GenerateChatTitleInput): Promise<GenerateChatTitleOutput> {
  return generateChatTitleFlow(input);
}

const generateChatTitlePrompt = ai.definePrompt({
  name: 'generateChatTitlePrompt',
  input: {schema: GenerateChatTitleInputSchema},
  output: {schema: GenerateChatTitleOutputSchema},
  prompt: `Generate a very short, concise title (3-5 words maximum) for a chat session that starts with the following user prompt. The title should summarize the core topic of the prompt.

User Prompt: {{{prompt}}}
`,
  model: 'gemini-2.0-flash',
});

const generateChatTitleFlow = ai.defineFlow(
  {
    name: 'generateChatTitleFlow',
    inputSchema: GenerateChatTitleInputSchema,
    outputSchema: GenerateChatTitleOutputSchema,
  },
  async input => {
    const {output} = await generateChatTitlePrompt(input);
    return output!;
  }
);
