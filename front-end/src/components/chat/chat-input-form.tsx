'use client';

import * as React from 'react';
import { type UseFormReturn } from 'react-hook-form';
import { z } from 'zod';
import { Form, FormControl, FormField, FormItem } from '@/components/ui/form';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { ArrowUp, Paperclip, Mic, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

const chatSchema = z.object({
  message: z.string().min(1, 'Message cannot be empty.'),
});

type ChatForm = z.infer<typeof chatSchema>;

interface ChatInputFormProps {
  form: UseFormReturn<ChatForm>;
  onSubmit: (data: ChatForm) => Promise<void>;
  isLoading: boolean;
}

export function ChatInputForm({ form, onSubmit, isLoading }: ChatInputFormProps) {
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const messageValue = form.watch('message');

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      if (!isLoading && form.formState.isValid) {
        form.handleSubmit(onSubmit)();
      }
    }
  };

  React.useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const maxHeight = 200; // 200px max height
      textareaRef.current.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
    }
  }, [messageValue]);

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <div className="relative flex w-full items-end rounded-lg border bg-secondary/50 pr-28 focus-within:ring-2 focus-within:ring-primary/50">
          <FormField
            control={form.control}
            name="message"
            render={({ field }) => (
              <FormItem className="flex-1">
                <FormControl>
                  <Textarea
                    {...field}
                    ref={textareaRef}
                    placeholder="Ask anything..."
                    className={cn(
                      'min-h-0 max-h-[200px] resize-none self-center border-0 bg-transparent px-4 py-3 text-base shadow-none focus-visible:ring-0 text-foreground placeholder:text-muted-foreground'
                    )}
                    onKeyDown={handleKeyDown}
                    rows={1}
                  />
                </FormControl>
              </FormItem>
            )}
          />
          <div className="absolute bottom-2 right-2 flex items-center gap-1">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button type="button" variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground">
                    <Paperclip className="h-5 w-5" />
                    <span className="sr-only">Attach file</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Attach file</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button type="button" variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground">
                    <Mic className="h-5 w-5" />
                    <span className="sr-only">Use microphone</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Use microphone</TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <Button
              type="submit"
              size="icon"
              className="h-8 w-8 shrink-0 rounded-full bg-primary hover:bg-primary/90"
              disabled={isLoading || !form.formState.isValid}
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <ArrowUp className="h-5 w-5" />
              )}
              <span className="sr-only">Send message</span>
            </Button>
          </div>
        </div>
      </form>
    </Form>
  );
}
