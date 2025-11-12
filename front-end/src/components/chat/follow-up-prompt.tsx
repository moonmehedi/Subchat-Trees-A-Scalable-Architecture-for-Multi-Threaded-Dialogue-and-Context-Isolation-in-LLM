
'use client';

import * as React from 'react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { BotIcon } from '../icons';

interface FollowUpPromptProps {
  children: React.ReactNode;
  onPromptClick: (prompt: string, sourceChatId: string) => void;
  chatId: string;
}

export function FollowUpPrompt({ children, onPromptClick, chatId }: FollowUpPromptProps) {
  const [selection, setSelection] = React.useState<string | null>(null);
  const [popoverPosition, setPopoverPosition] = React.useState({ top: 0, left: 0, width: 0, height: 0 });
  const contentRef = React.useRef<HTMLDivElement>(null);
  const [isOpen, setIsOpen] = React.useState(false);

  const handleMouseUp = () => {
    // Timeout to allow the browser to register the selection
    setTimeout(() => {
      const sel = window.getSelection();
      if (sel && !sel.isCollapsed && contentRef.current) {
        const selectedText = sel.toString().trim();
        if (selectedText) {
          const range = sel.getRangeAt(0);
          const rect = range.getBoundingClientRect();
          const containerRect = contentRef.current.getBoundingClientRect();
          
          setPopoverPosition({
            top: rect.top - containerRect.top,
            left: rect.left - containerRect.left,
            width: rect.width,
            height: rect.height
          });
          setSelection(selectedText);
          setIsOpen(true);
        }
      } else {
        setSelection(null);
        setIsOpen(false);
      }
    }, 10);
  };
  
  const handlePrompt = () => {
    if (selection) {
      onPromptClick(`Tell me more about "${selection}"`, chatId);
    }
    setIsOpen(false);
    setSelection(null);
  };
  
  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setIsOpen(false);
      setSelection(null);
      if (window.getSelection) {
        window.getSelection()?.removeAllRanges();
      }
    }
  };

  return (
    <div ref={contentRef} onMouseUp={handleMouseUp} className="relative">
      <Popover open={isOpen} onOpenChange={handleOpenChange}>
        <PopoverTrigger asChild>
           <div 
             style={{
               position: 'absolute',
               top: `${popoverPosition.top}px`,
               left: `${popoverPosition.left}px`,
               width: `${popoverPosition.width}px`,
               height: `${popoverPosition.height}px`,
             }} 
           />
        </PopoverTrigger>
        <PopoverContent
            className="w-auto p-1"
            side="top"
            align="center"
            sideOffset={4}
            onOpenAutoFocus={(e) => e.preventDefault()}
        >
            <Button onClick={handlePrompt} size="sm" variant="default">
                <BotIcon className="mr-2 h-4 w-4" />
                Ask InsightFlow
            </Button>
        </PopoverContent>
      </Popover>
      {children}
    </div>
  );
}
