
'use client';

import * as React from 'react';
import { Sidebar } from '@/components/sidebar';
import { cn } from '@/lib/utils';
import type { Message, ChatSession } from '@/lib/types';
import { getAiResponse, getAiTitle } from '@/app/actions';
import { useToast } from '@/hooks/use-toast';
import { Welcome } from '@/components/chat/welcome';
import { ChatLayout } from '@/components/chat/chat-layout';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ChatCarousel } from '@/components/chat/chat-carousel';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

const chatSchema = z.object({
  message: z.string().min(1, 'Message cannot be empty.'),
});

type ChatForm = z.infer<typeof chatSchema>;


export default function Home() {
  const [isClient, setIsClient] = React.useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);
  const { toast } = useToast();

  const [chatSessions, setChatSessions] = React.useState<ChatSession[]>([]);
  const [visibleChatIds, setVisibleChatIds] = React.useState<string[]>([]);
  const [currentChatIndex, setCurrentChatIndex] = React.useState(0);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = React.useState(false);
  const [chatToDelete, setChatToDelete] = React.useState<string | null>(null);

  const form = useForm<ChatForm>({
    resolver: zodResolver(chatSchema),
    defaultValues: {
      message: '',
    },
  });

  React.useEffect(() => {
    setIsClient(true);
  }, []);

  const getBranchForChat = (chatId: string, allChats: ChatSession[]): string[] => {
    const branch: string[] = [];
    let currentChat: ChatSession | undefined = allChats.find(c => c.id === chatId);
    const visited = new Set<string>();

    // Go up to the root
    while(currentChat && currentChat.parentId && !visited.has(currentChat.id)) {
        visited.add(currentChat.id);
        const parent = allChats.find(c => c.id === currentChat!.parentId);
        if (parent) {
            branch.unshift(parent.id);
            currentChat = parent;
        } else {
            break;
        }
    }

    // Add the chat itself if it's not there
    if(!branch.includes(chatId)){
        branch.push(chatId);
    }

    // Go down to the most active child branch
    let currentLeafId = chatId;
    let child: ChatSession | undefined;

    while (true) {
        const children = allChats.filter(c => c.parentId === currentLeafId);
        if (children.length > 0) {
            // Simplified logic: follow the first child.
            // A more complex app might use timestamps to find the most recent branch.
            child = children[0];
            branch.push(child.id);
            currentLeafId = child.id;
        } else {
            break;
        }
    }
    
    return branch;
  }

  const setActiveChat = (chatId: string) => {
    const branchIds = getBranchForChat(chatId, chatSessions);
    const selectedChatIndexInBranch = branchIds.indexOf(chatId);

    if (selectedChatIndexInBranch !== -1) {
        setVisibleChatIds(branchIds);
        setCurrentChatIndex(selectedChatIndexInBranch);
    } else {
       // Fallback for safety, though this shouldn't happen with correct logic
       setVisibleChatIds([chatId]);
       setCurrentChatIndex(0);
    }
  }


  const createNewChat = async (prompt?: string) => {
    const newChatId = `chat-${Date.now()}`;
    
    const title = prompt ? (await getAiTitle({ prompt })).title : 'New Chat';

    const newSession: ChatSession = {
      id: newChatId,
      title: title,
      messages: [],
      isLoading: false,
    };

    setChatSessions(prev => [...prev, newSession]);
    setVisibleChatIds([newChatId]);
    setCurrentChatIndex(0);

    if (prompt) {
      // Use a timeout to ensure state has updated before submitting
      setTimeout(() => handleSubmit(newChatId, prompt), 0);
    }
  };
  
  const handleRelatedTopicClick = async (prompt: string, sourceChatId: string) => {
    const newChatId = `chat-${Date.now()}`;
    const selectedTextForTitle = prompt.match(/Tell me more about "([^"]*)"/)?.[1] || prompt;
    const titleResponse = await getAiTitle({ prompt: selectedTextForTitle });

    const newSession: ChatSession = {
      id: newChatId,
      title: titleResponse.title,
      messages: [],
      isLoading: false,
      parentId: sourceChatId,
    };

    const updatedSessions = [...chatSessions, newSession];
    setChatSessions(updatedSessions);

    const newVisibleIds = [sourceChatId, newChatId];
    setVisibleChatIds(newVisibleIds);
    setCurrentChatIndex(1); // Show the new chat on the right
    
    // Use a timeout to ensure state has updated before submitting
    setTimeout(() => handleSubmit(newChatId, prompt), 0);
  };

  const handleSubmit = async (chatId: string, userInput: string) => {
    if (!userInput) return;
    
    const currentChatId = chatId || visibleChatIds[currentChatIndex];
    if (!currentChatId) {
        console.error("handleSubmit called with no active chat.");
        return;
    }

    setChatSessions((prev) =>
      prev.map((session) =>
        session.id === currentChatId
          ? {
              ...session,
              messages: [
                ...session.messages,
                {
                  id: String(Date.now()),
                  role: 'user',
                  content: userInput,
                },
              ],
              isLoading: true,
            }
          : session
      )
    );

    try {
        const aiResponsePromise = getAiResponse(userInput);

        const chatBeforeUpdate = chatSessions.find(c => c.id === currentChatId);
        const isFirstMessage = chatBeforeUpdate && chatBeforeUpdate.messages.length === 0;

        const titlePromise = isFirstMessage 
            ? getAiTitle({ prompt: userInput }) 
            : Promise.resolve({ title: chatBeforeUpdate?.title || '' });
        
        const [aiResponse, titleResponse] = await Promise.all([aiResponsePromise, titlePromise]);

      const assistantMessage: Message = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: aiResponse.response,
        sources: aiResponse.sources,
        relatedTopics: aiResponse.relatedTopics,
      };

      setChatSessions((prev) =>
        prev.map((session) =>
          session.id === currentChatId
            ? { ...session, messages: [...session.messages, assistantMessage], isLoading: false, title: isFirstMessage ? titleResponse.title : session.title }
            : session
        )
      );
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to get a response from the AI.',
      });
       setChatSessions((prev) =>
        prev.map((session) =>
          session.id === currentChatId ? { ...session, isLoading: false } : session
        )
      );
    }
  };

  const handleFormSubmit = async (data: ChatForm) => {
    const activeChatId = visibleChatIds[currentChatIndex]
    if (!activeChatId) {
        await createNewChat(data.message);
    } else {
        await handleSubmit(activeChatId, data.message);
    }
    form.reset();
  };
  
  const getVisibleChats = () => {
    if (visibleChatIds.length === 0) return [];
    
    const startIndex = Math.max(0, currentChatIndex - 1);
    const endIndex = Math.min(visibleChatIds.length, currentChatIndex + 1);
    
    let chatIdsToShow = visibleChatIds.slice(startIndex, endIndex);

    // If we're at the beginning of the branch and there's a next chat, show it.
    if (chatIdsToShow.length === 1 && currentChatIndex === 0 && visibleChatIds.length > 1) {
        chatIdsToShow.push(visibleChatIds[1]);
    }
    // If we have only one chat in the view, but we are not at the start, show the previous one.
    else if (chatIdsToShow.length === 1 && currentChatIndex > 0) {
      chatIdsToShow.unshift(visibleChatIds[currentChatIndex - 1]);
    } else if (chatIdsToShow.length === 0 && visibleChatIds.length > 0) {
      // Fallback if index is out of sync
      chatIdsToShow = [visibleChatIds[currentChatIndex]];
    }

    const chats = chatIdsToShow
      .map(id => chatSessions.find(c => c.id === id))
      .filter((c): c is ChatSession => !!c);
        
    return chats;
  };

  const promptDeleteChat = (chatId: string) => {
    setChatToDelete(chatId);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteChat = () => {
    if (!chatToDelete) return;

    setChatSessions(prev => {
        const chatsToDelete = new Set<string>([chatToDelete]);
        let children = prev.filter(c => c.parentId === chatToDelete);
        while(children.length > 0) {
            const childIds = children.map(c => c.id);
            childIds.forEach(id => chatsToDelete.add(id));
            children = prev.filter(c => childIds.includes(c.parentId || ''));
        }

        const newSessions = prev.filter(c => !chatsToDelete.has(c.id));
        const newVisibleIds = visibleChatIds.filter(id => !chatsToDelete.has(id));
        
        if (newVisibleIds.length !== visibleChatIds.length) {
            if(newVisibleIds.length === 0) {
                setVisibleChatIds([]);
                setCurrentChatIndex(0);
            } else {
                const newIndex = Math.max(0, currentChatIndex - 1);
                setVisibleChatIds(newVisibleIds);
                setCurrentChatIndex(newIndex);
            }
        } else if (visibleChatIds.length > 0 && newVisibleIds.length === 0) {
             setVisibleChatIds([]);
             setCurrentChatIndex(0);
        }
        
        return newSessions;
    });

    setIsDeleteDialogOpen(false);
    setChatToDelete(null);
  };

  const handleRenameChat = (chatId: string, newTitle: string) => {
    if (newTitle) {
      setChatSessions(prev =>
        prev.map(chat =>
          chat.id === chatId ? { ...chat, title: newTitle } : chat
        )
      );
    }
  };
  
  if (!isClient) {
    return null;
  }

  const visibleChats = getVisibleChats();
  const isLoading = visibleChats.some(chat => chat.isLoading);

  return (
    <div className="relative h-screen w-full">
      <div
        className={cn(
          'grid h-full w-full overflow-hidden',
           isSidebarOpen ? 'grid-cols-[18rem_1fr]' : 'grid-cols-[4.5rem_1fr]',
           'transition-all duration-300'
        )}
      >
        <Sidebar
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
          onNewChat={() => createNewChat()}
          chatHistory={chatSessions}
          activeChatId={visibleChatIds[currentChatIndex]}
          setActiveChatId={setActiveChat}
          onDeleteChat={promptDeleteChat}
          onRenameChat={handleRenameChat}
        />
        <main className={cn("relative flex h-full flex-col overflow-hidden")}>
           { visibleChats.length === 0 ? (
              <ChatLayout 
                  form={form}
                  onSubmit={handleFormSubmit}
                  isLoading={false}
              >
                  <Welcome onExampleClick={(prompt) => createNewChat(prompt)} />
              </ChatLayout>
           ) : (
              <ChatCarousel
                chats={visibleChats}
                onSubmit={handleSubmit}
                onRelatedTopicClick={handleRelatedTopicClick}
                currentChatIndex={currentChatIndex}
                setCurrentChatIndex={setCurrentChatIndex}
                totalChatsInBranch={visibleChatIds.length}
              />
           )}
        </main>
      </div>
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete this
              chat session and all of its child messages.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteChat}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
