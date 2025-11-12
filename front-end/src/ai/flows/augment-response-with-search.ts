'use server';
/**
 * @fileOverview An AI agent that augments responses with relevant URLs from web search.
 *
 * - augmentResponseWithSearch - A function that handles the augmentation process.
 * - AugmentResponseWithSearchInput - The input type for the augmentResponseWithSearch function.
 * - AugmentResponseWithSearchOutput - The return type for the augmentResponseWithSearch function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const AugmentResponseWithSearchInputSchema = z.object({
  query: z.string().describe('The user query to augment with search results.'),
  response: z.string().describe('The initial response from the AI chatbot.'),
});
export type AugmentResponseWithSearchInput = z.infer<typeof AugmentResponseWithSearchInputSchema>;

const AugmentResponseWithSearchOutputSchema = z.object({
  augmentedResponse: z.string().describe('The augmented response with search results.'),
  sourceUrls: z.array(z.string()).describe('The list of source URLs used to augment the response.'),
});
export type AugmentResponseWithSearchOutput = z.infer<typeof AugmentResponseWithSearchOutputSchema>;

export async function augmentResponseWithSearch(input: AugmentResponseWithSearchInput): Promise<AugmentResponseWithSearchOutput> {
  return augmentResponseWithSearchFlow(input);
}

const searchWeb = ai.defineTool({
  name: 'searchWeb',
  description: 'Searches the web for relevant information based on the user query.',
  inputSchema: z.object({
    query: z.string().describe('The search query.'),
  }),
  outputSchema: z.array(z.string()).describe('A list of URLs from the search results.'),
},
async (input) => {
  // Placeholder implementation for web search.
  // In a real application, this would integrate with a search engine API.
  // For now, return a hardcoded list of URLs.
  console.log('Searching the web for:', input.query);
  return [
    'https://example.com/search-result-1',
    'https://example.com/search-result-2',
    'https://example.com/search-result-3',
  ];
});

const augmentResponseWithSearchPrompt = ai.definePrompt({
  name: 'augmentResponseWithSearchPrompt',
  tools: [searchWeb],
  input: {schema: AugmentResponseWithSearchInputSchema},
  output: {schema: AugmentResponseWithSearchOutputSchema},
  prompt: `You are an AI chatbot that augments its responses with information from web search results.

  You have already provided an initial response to the user's query. Now, use the searchWeb tool to find relevant URLs that can supplement your answer with current information.

  User Query: {{{query}}}
  Initial Response: {{{response}}}

  Include the relevant information from the search results in your augmented response. Also, provide a list of the source URLs used to augment the response.

  If the user's question asks about a public company, include its stock price in your answer, using the searchWeb tool to get the current price.
  `,
});

const augmentResponseWithSearchFlow = ai.defineFlow(
  {
    name: 'augmentResponseWithSearchFlow',
    inputSchema: AugmentResponseWithSearchInputSchema,
    outputSchema: AugmentResponseWithSearchOutputSchema,
  },
  async input => {
    const {output} = await augmentResponseWithSearchPrompt(input);
    return output!;
  }
);
