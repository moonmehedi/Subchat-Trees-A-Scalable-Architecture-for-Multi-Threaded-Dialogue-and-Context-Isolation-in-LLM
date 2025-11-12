import type { GenerateChatbotResponseOutput } from '@/ai/flows/generate-chatbot-response';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: GenerateChatbotResponseOutput['sources'];
  relatedTopics?: GenerateChatbotResponseOutput['relatedTopics'];
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  isLoading: boolean;
  parentId?: string;
}
