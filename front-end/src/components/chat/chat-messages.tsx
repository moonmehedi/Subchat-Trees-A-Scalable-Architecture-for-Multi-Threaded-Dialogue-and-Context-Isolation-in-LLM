
'use client';

import * as React from 'react';
import type { Message } from '@/lib/types';
import { Welcome } from './welcome';
import { ChatMessage } from './chat-message';
import { Skeleton } from '@/components/ui/skeleton';
import { BotIcon } from '../icons';
import { Avatar, AvatarFallback } from '../ui/avatar';

interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
  onRelatedTopicClick: (prompt: string, sourceChatId: string) => void;
  onExampleClick: (prompt: string, sourceChatId: string) => void;
  chatId: string;
}

export function ChatMessages({ messages, isLoading, onRelatedTopicClick, chatId, onExampleClick }: ChatMessagesProps) {
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
      <div className="w-full">
        {messages.length === 0 && !isLoading ? (
          <Welcome onExampleClick={(prompt) => onExampleClick(prompt, chatId)} />
        ) : (
          <div className="flex flex-col gap-8">
            {messages.map((message, index) => {
              const isLastMessage = index === messages.length - 1;
              const isStreamingMessage = isLoading && isLastMessage && message.role === 'assistant';
              
              return (
                <ChatMessage
                  key={message.id}
                  message={message}
                  onRelatedTopicClick={onRelatedTopicClick}
                  chatId={chatId}
                  isStreaming={isStreamingMessage}
                />
              );
            })}
            {isLoading && messages.length === 0 && (
              <div className="flex items-start gap-4">
                <Avatar className="h-8 w-8 border">
                  <AvatarFallback>
                    <BotIcon className="h-5 w-5" />
                  </AvatarFallback>
                </Avatar>
                <div className="flex flex-col gap-2">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-4 w-64" />
                  <Skeleton className="h-4 w-56" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
  );
}
