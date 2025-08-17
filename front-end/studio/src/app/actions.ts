
'use server';

import { generateChatbotResponse, type GenerateChatbotResponseOutput } from '@/ai/flows/generate-chatbot-response';
import { generateChatTitle, type GenerateChatTitleInput, type GenerateChatTitleOutput } from '@/ai/flows/generate-chat-title';

export type AiResponse = GenerateChatbotResponseOutput;

export async function getAiResponse(userInput: string): Promise<AiResponse> {
    try {
        const aiResponse = await generateChatbotResponse({
            prompt: userInput,
        });

        return aiResponse;

    } catch (error) {
        console.error('Error generating AI response:', error);
        // In case of an error, return a message that can be displayed to the user.
        return {
            response: "Sorry, I encountered an error and couldn't process your request. Please try again later.",
            sources: [],
            relatedTopics: [],
        };
    }
}

export async function getAiTitle(input: GenerateChatTitleInput): Promise<GenerateChatTitleOutput> {
    try {
        const titleResponse = await generateChatTitle(input);

        return titleResponse;

    } catch (error) {
        console.error('Error generating AI title:', error);
        // In case of an error, return a fallback title.
        return {
            title: input.prompt.substring(0, 30) + '...',
        };
    }
}
