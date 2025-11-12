
'use client';

import type { Message } from '@/lib/types';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { User, ChevronsRight } from 'lucide-react';
import { BotIcon } from '../icons';
import { Button } from '../ui/button';
import { FollowUpPrompt } from './follow-up-prompt';
import { MarkdownRenderer } from '../markdown-renderer';

interface ChatMessageProps {
  message: Message;
  onRelatedTopicClick: (prompt: string, sourceChatId: string) => void;
  chatId: string;
  isStreaming?: boolean;
}

export function ChatMessage({ message, onRelatedTopicClick, chatId, isStreaming = false }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className="flex w-full items-start gap-4">
       <Avatar className="h-8 w-8 shrink-0 border">
          <AvatarFallback>
            {isUser ? <User className="h-5 w-5" /> : <BotIcon className="h-5 w-5" />}
          </AvatarFallback>
        </Avatar>
      <div className="flex-1 space-y-2">
        <div className="font-bold">{isUser ? 'You' : 'InsightFlow'}</div>
        <div className="prose dark:prose-invert max-w-full text-current break-words">
            <FollowUpPrompt onPromptClick={onRelatedTopicClick} chatId={chatId}>
              {isUser ? (
                <div className="text-white">
                  {message.content}
                </div>
              ) : (
                <MarkdownRenderer 
                  content={message.content} 
                  isStreaming={isStreaming}
                />
              )}
            </FollowUpPrompt>
        </div>
        {!isUser && message.relatedTopics && message.relatedTopics.length > 0 && (
          <div className="pt-4">
              <div className='flex items-center gap-1 mb-2'>
                <ChevronsRight className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-semibold text-muted-foreground">
                  Related
                </span>
              </div>
            <div className="flex flex-wrap gap-2">
              {message.relatedTopics.map((topic, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="text-sm h-auto py-1.5 px-3"
                  onClick={() => onRelatedTopicClick(topic.title, chatId)}
                >
                  {topic.title}
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
