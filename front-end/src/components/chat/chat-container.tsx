
'use client';

import * as React from 'react';
import type { ChatSession } from '@/lib/types';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ChatLayout } from './chat-layout';
import { ChatMessages } from './chat-messages';
import { Welcome } from './welcome';

interface ChatContainerProps {
  chatSession: ChatSession;
  onSubmit: (chatId: string, message: string) => Promise<void>;
  onRelatedTopicClick: (prompt: string, sourceChatId: string) => void;
}

const chatSchema = z.object({
  message: z.string().min(1, 'Message cannot be empty.'),
});

type ChatForm = z.infer<typeof chatSchema>;

export function ChatContainer({
  chatSession,
  onSubmit,
  onRelatedTopicClick,
}: ChatContainerProps) {
  
  const form = useForm<ChatForm>({
    resolver: zodResolver(chatSchema),
    defaultValues: {
      message: '',
    },
  });

  const handleFormSubmit = async (data: ChatForm) => {
    await onSubmit(chatSession.id, data.message);
    form.reset();
  };
  
  return (
    <ChatLayout
      form={form}
      onSubmit={handleFormSubmit}
      isLoading={chatSession.isLoading}
    >
        {chatSession.messages.length > 0 || chatSession.isLoading ? (
            <ChatMessages 
                messages={chatSession.messages}
                isLoading={chatSession.isLoading}
                onRelatedTopicClick={onRelatedTopicClick}
                chatId={chatSession.id}
                onExampleClick={(prompt) => onSubmit(chatSession.id, prompt)}
            />
        ) : (
             <Welcome onExampleClick={(prompt) => onSubmit(chatSession.id, prompt)} />
        )}
    </ChatLayout>
  );
}
