'use server';

/**
 * @fileOverview This file defines the generateChatbotResponse flow, which generates responses to user prompts using a Large Language Model, optionally augmenting the response with web search results.
 *
 * @exports generateChatbotResponse - The main function to generate chatbot responses.
 * @exports GenerateChatbotResponseInput - The input type for the generateChatbotResponse function.
 * @exports GenerateChatbotResponseOutput - The output type for the generateChatbotResponse function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SearchResultSchema = z.object({
  title: z.string(),
  url: z.string(),
  snippet: z.string(),
});

const WebSearchToolInputSchema = z.object({
  query: z.string().describe('The search query to use.'),
});

const WebSearchToolOutputSchema = z.array(SearchResultSchema);

const webSearch = ai.defineTool(
  {
    name: 'webSearch',
    description: 'Performs a web search and returns a list of search results.',
    inputSchema: WebSearchToolInputSchema,
    outputSchema: WebSearchToolOutputSchema,
  },
  async input => {
    // This is a placeholder implementation. Replace with actual web search logic.
    console.log(`Performing web search for: ${input.query}`);
    return [
      {
        title: 'Example Search Result 1',
        url: 'https://example.com/result1',
        snippet: 'This is an example search result snippet.',
      },
      {
        title: 'Example Search Result 2',
        url: 'https://example.com/result2',
        snippet: 'This is another example search result snippet.',
      },
    ];
  }
);

const GenerateChatbotResponseInputSchema = z.object({
  prompt: z.string().describe('The user prompt or question.'),
});

export type GenerateChatbotResponseInput = z.infer<
  typeof GenerateChatbotResponseInputSchema
>;

const GenerateChatbotResponseOutputSchema = z.object({
  response: z.string().describe('The chatbot response to the user prompt.'),
  sources: z.array(SearchResultSchema).optional().describe('The list of source URLs used to generate the response.'),
  relatedTopics: z.array(z.object({title: z.string()})).optional().describe('A list of 3-4 suggested follow-up questions or related topics.'),
});

export type GenerateChatbotResponseOutput = z.infer<
  typeof GenerateChatbotResponseOutputSchema
>;

export async function generateChatbotResponse(
  input: GenerateChatbotResponseInput
): Promise<GenerateChatbotResponseOutput> {
  return generateChatbotResponseFlow(input);
}

const generateChatbotResponsePrompt = ai.definePrompt({
  name: 'generateChatbotResponsePrompt',
  input: {
    schema: GenerateChatbotResponseInputSchema,
  },
  output: {
    schema: GenerateChatbotResponseOutputSchema,
  },
  tools: [webSearch],
  prompt: `You are a helpful and informative chatbot. Your goal is to provide accurate and relevant responses to user prompts. If relevant, use the available tools to supplement your answers with current information from the web.

After your main response, you MUST suggest 3-4 follow-up questions or related topics that the user might be interested in. This helps guide the conversation and offers further exploration.

User Prompt: {{{prompt}}}
`,
  model: 'gemini-2.0-flash',
});

const generateChatbotResponseFlow = ai.defineFlow(
  {
    name: 'generateChatbotResponseFlow',
    inputSchema: GenerateChatbotResponseInputSchema,
    outputSchema: GenerateChatbotResponseOutputSchema,
  },
  async input => {
    const {output} = await generateChatbotResponsePrompt(input);
    return output!;
  }
);
