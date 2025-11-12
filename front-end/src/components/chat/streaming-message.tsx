import React, { useState, useEffect } from 'react';
import { MarkdownRenderer } from '../markdown-renderer';
import { Message } from '@/lib/types';

interface StreamingMessageProps {
  message: Message;
  isStreaming: boolean;
}

export function StreamingMessage({ message, isStreaming }: StreamingMessageProps) {
  const [displayContent, setDisplayContent] = useState('');

  useEffect(() => {
    if (!isStreaming) {
      setDisplayContent(message.content);
      return;
    }

    // If streaming, animate the text appearance
    const content = message.content;
    let currentIndex = 0;
    
    const interval = setInterval(() => {
      if (currentIndex < content.length) {
        setDisplayContent(content.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 20); // Adjust speed as needed

    return () => clearInterval(interval);
  }, [message.content, isStreaming]);

  return (
    <div className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}>
      {message.role === 'user' ? (
        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="text-gray-900 dark:text-gray-100">
            {message.content}
          </div>
        </div>
      ) : (
        <div className="p-4">
          <MarkdownRenderer 
            content={displayContent} 
            isStreaming={isStreaming && displayContent.length < message.content.length}
          />
        </div>
      )}
    </div>
  );
}