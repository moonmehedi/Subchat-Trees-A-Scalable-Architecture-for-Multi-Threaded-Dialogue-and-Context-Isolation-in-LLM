
'use server';

import { HierarchicalChatAPI } from '@/lib/api-client';

// Initialize the API client
const chatAPI = new HierarchicalChatAPI();

export type AiResponse = {
    response: string;
    sources: any[];
    relatedTopics: { title: string }[];
    conversationTitle?: string;  // Backend provides updated title if generated
};

export async function getAiResponse(userInput: string, conversationId?: string): Promise<AiResponse & { conversationId?: string; newTitle?: string }> {
    try {
        let response;
        let newConversationId = conversationId;
        
        if (conversationId) {
            // Send message to existing conversation
            response = await chatAPI.sendMessage(conversationId, userInput);
        } else {
            // Create new conversation and send first message
            const newConversation = await chatAPI.createConversation();
            newConversationId = newConversation.node_id;
            response = await chatAPI.sendMessage(newConversationId, userInput);
        }

        return {
            response: response.response || "I received your message but couldn't generate a response.",
            sources: [], // Backend doesn't provide sources yet
            relatedTopics: [], // Backend doesn't provide related topics yet
            conversationId: newConversationId,
            newTitle: response.conversation_title // Title from backend if generated
        };

    } catch (error) {
        console.error('Error generating AI response:', error);
        // In case of an error, return a message that can be displayed to the user.
        return {
            response: "Sorry, I encountered an error and couldn't process your request. Please try again later.",
            sources: [],
            relatedTopics: [],
            conversationId
        };
    }
}

// 🧹 REMOVED: getAiTitle function - title generation now happens automatically in backend

// New function for creating subchats via backend
export async function createSubchat(parentConversationId: string, title: string): Promise<{ conversation_id: string; title: string }> {
    try {
        const subchatResponse = await chatAPI.createSubchat(parentConversationId, title);
        return subchatResponse;
    } catch (error) {
        console.error('Error creating subchat:', error);
        throw error;
    }
}
