
'use client'

import * as React from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatInputForm } from './chat-input-form';
import { UseFormReturn } from 'react-hook-form';
import { z } from 'zod';

const chatSchema = z.object({
  message: z.string().min(1, 'Message cannot be empty.'),
});

type ChatForm = z.infer<typeof chatSchema>;

interface ChatLayoutProps {
  children: React.ReactNode;
  form: UseFormReturn<ChatForm>;
  onSubmit: (data: ChatForm) => Promise<void>;
  isLoading: boolean;
}

export function ChatLayout({ children, form, onSubmit, isLoading }: ChatLayoutProps) {
  return (
    <div className="flex h-full w-full flex-col flex-1">
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="mx-auto w-full max-w-3xl px-4 py-8">
            {children}
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
  )
}
