
'use client';

import * as React from 'react';
import type { Message } from '@/lib/types';
import { ChatMessages } from './chat-messages';
import { ChatInputForm } from './chat-input-form';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useForm, type UseFormReturn } from 'react-hook-form';
import { z } from 'zod';

const chatSchema = z.object({
  message: z.string().min(1, 'Message cannot be empty.'),
});

type ChatForm = z.infer<typeof chatSchema>;

interface ChatPanelProps {
  chatId: string;
  messages: Message[];
  isLoading: boolean;
  onRelatedTopicClick: (prompt: string, sourceChatId: string) => void;
  form: UseFormReturn<ChatForm>;
  onSubmit: (data: ChatForm) => Promise<void>;
}


export function ChatPanel({ chatId, messages, isLoading, onRelatedTopicClick, form, onSubmit }: ChatPanelProps) {

  const handleFollowUp = (topic: string, sourceChatId: string) => {
    onRelatedTopicClick(topic, sourceChatId);
  }

  return (
    <div className="flex h-full w-full flex-col">
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="mx-auto w-full max-w-3xl px-4 py-8">
              <ChatMessages
                  messages={messages}
                  isLoading={isLoading}
                  onRelatedTopicClick={handleFollowUp}
                  chatId={chatId}
              />
          </div>
        </ScrollArea>
      </div>
      <div className="bg-background/80 pb-4 pt-2 backdrop-blur-md">
        <div className="mx-auto max-w-2xl px-4">
          <ChatInputForm form={form} onSubmit={onSubmit} isLoading={isLoading} />
          <p className="mt-2 text-center text-xs text-muted-foreground">
            InsightFlow can make mistakes. Consider checking important information.
          </p>
        </div>
      </div>
    </div>
  );
}
