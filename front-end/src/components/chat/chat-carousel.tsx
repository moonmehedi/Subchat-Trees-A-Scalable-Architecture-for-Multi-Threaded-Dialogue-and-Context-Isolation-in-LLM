
'use client';

import * as React from 'react';
import type { ChatSession } from '@/lib/types';
import { ChatContainer } from './chat-container';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Separator } from '../ui/separator';

interface ChatCarouselProps {
  chats: ChatSession[];
  onSubmit: (chatId: string, message: string) => Promise<void>;
  onRelatedTopicClick: (prompt: string, sourceChatId: string) => void;
  currentChatIndex: number;
  setCurrentChatIndex: (index: number) => void;
  totalChatsInBranch: number;
}

export function ChatCarousel({
  chats,
  onSubmit,
  onRelatedTopicClick,
  currentChatIndex,
  setCurrentChatIndex,
  totalChatsInBranch,
}: ChatCarouselProps) {
  const containerRef = React.useRef<HTMLDivElement>(null);

  const canGoLeft = currentChatIndex > 0;
  // This logic is tricky. The `chats` array only holds up to 2 chats.
  // The actual ability to go right depends on the total number of chats in the branch.
  const canGoRight = currentChatIndex < totalChatsInBranch - 1 && chats.length > 1;

  const handleNav = (direction: 'left' | 'right') => {
    const newIndex = direction === 'left' ? currentChatIndex - 1 : currentChatIndex + 1;
    setCurrentChatIndex(newIndex);
  };
  
  React.useEffect(() => {
    if (containerRef.current) {
        containerRef.current.scrollTo({ left: 0, behavior: 'instant' });
    }
  }, [currentChatIndex]);


  if (chats.length === 0) {
    return null;
  }
  
  const isMultiView = chats.length > 1;

  return (
    <div className="relative flex h-full w-full flex-1 overflow-hidden">
      {canGoLeft && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute left-2 top-1/2 z-10 -translate-y-1/2 rounded-full bg-background/50 backdrop-blur-sm"
          onClick={() => handleNav('left')}
        >
          <ChevronLeft className="h-5 w-5" />
        </Button>
      )}

      <div ref={containerRef} className={cn("flex h-full w-full flex-row overflow-hidden")}>
        {chats.map((chat, index) => (
          <React.Fragment key={chat.id}>
            <div className="flex-shrink-0" style={{ width: isMultiView ? '50%' : '100%'}}>
              <ChatContainer
                chatSession={chat}
                onSubmit={onSubmit}
                onRelatedTopicClick={onRelatedTopicClick}
              />
            </div>
            {index < chats.length - 1 && isMultiView && (
                <Separator orientation="vertical" className="h-full" />
            )}
          </React.Fragment>
        ))}
      </div>

      {canGoRight && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute right-2 top-1/2 z-10 -translate-y-1/2 rounded-full bg-background/50 backdrop-blur-sm"
          onClick={() => handleNav('right')}
        >
          <ChevronRight className="h-5 w-5" />
        </Button>
      )}
    </div>
  );
}

    
