
'use client';

import * as React from 'react';
import { Sidebar } from '@/components/sidebar';
import { cn } from '@/lib/utils';
import type { Message, ChatSession } from '@/lib/types';
// 🧹 REMOVED: getAiTitle import - title generation now automatic
import { HierarchicalChatAPI } from '@/lib/api-client';
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
  
  // Initialize API client on client side
  const [chatAPI] = React.useState(() => new HierarchicalChatAPI());

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
    const currentChat = allChats.find(c => c.id === chatId);
    if (!currentChat) {
      console.warn('🐛 getBranchForChat: Chat not found:', chatId);
      return [chatId]; // Return the chatId to prevent completely empty arrays
    }

    // Build the path from current chat to root (walking up the parent chain)
    const pathToRoot: string[] = [];
    let current = currentChat;
    const visited = new Set<string>();

    // Walk up to root, collecting IDs
    while (current && !visited.has(current.id)) {
      visited.add(current.id);
      pathToRoot.unshift(current.id); // Add at beginning to maintain root→child order
      
      if (current.parentId) {
        const parent = allChats.find(c => c.id === current.parentId);
        if (parent) {
          current = parent;
        } else {
          console.warn('🐛 getBranchForChat: Parent not found:', current.parentId);
          break;
        }
      } else {
        break; // Reached root
      }
    }

    console.log('🐛 getBranchForChat result:', { 
      requestedChatId: chatId, 
      foundPath: pathToRoot,
      totalChats: allChats.length,
      currentChatTitle: currentChat.title
    });
    
    return pathToRoot;
  }

  const setActiveChat = (chatId: string) => {
    if (!chatId || chatId === 'undefined') {
      console.error('🐛 setActiveChat called with invalid chatId:', chatId);
      return;
    }
    
    console.log('🐛 setActiveChat called with:', chatId);
    const branchIds = getBranchForChat(chatId, chatSessions);
    const selectedChatIndexInBranch = branchIds.indexOf(chatId);

    console.log('🐛 setActiveChat result:', {
      chatId,
      branchIds,
      selectedChatIndexInBranch,
      totalSessions: chatSessions.length
    });

    if (selectedChatIndexInBranch !== -1) {
        setVisibleChatIds(branchIds);
        setCurrentChatIndex(selectedChatIndexInBranch);
    } else {
       // Fallback: if somehow the chat isn't in its own branch, show just that chat
       console.warn('🐛 setActiveChat fallback triggered for chatId:', chatId);
       setVisibleChatIds([chatId]);
       setCurrentChatIndex(0);
    }
  }


    const createNewChat = async (prompt?: string) => {
    // Create a temporary session while we create the backend conversation
    const tempChatId = `temp-${Date.now()}`;

    const newSession: ChatSession = {
      id: tempChatId,
      title: 'New Chat', // Default title, will be auto-generated on first message
      messages: [],
      isLoading: false,
    };

    const updatedSessions = [...chatSessions, newSession];
    setChatSessions(updatedSessions);
    setVisibleChatIds([tempChatId]);
    setCurrentChatIndex(0);

    if (prompt) {
      // Use a timeout to ensure state has updated before submitting
      setTimeout(() => handleSubmit(tempChatId, prompt), 0);
    }
  };
  
  const handleRelatedTopicClick = async (prompt: string, sourceChatId: string) => {
    try {
      console.log('🐛 Starting subchat creation:', { prompt, sourceChatId });
      
      // Extract the selected text from the prompt (what user actually selected)
      const selectedTextForTitle = prompt.match(/Tell me more about "([^"]*)"/)?.[1] || prompt;
      console.log('🐛 Extracted selected text for title:', selectedTextForTitle);

      // 🧹 CLEAN: Create subchat with default "New Chat" title - AI will generate title on first message
      const subchatResponse = await chatAPI.createSubchat(
        sourceChatId,                    // Parent conversation ID
        "New Chat",                      // Default title - will be auto-generated by AI
        selectedTextForTitle,            // The actual text user selected (for AI context)
        "explore this topic in detail",  // What user wants to do (follow-up intent)
        "follow_up"                      // Type of conversation
      );
      
      const newChatId = subchatResponse.node_id;
      console.log('🐛 Backend subchat created with context:', { 
        newChatId, 
        title: "New Chat", // Will be auto-generated
        selectedText: selectedTextForTitle 
      });

      const newSession: ChatSession = {
        id: newChatId,
        title: "New Chat", // Will be auto-generated on first message
        messages: [], // 🧹 CLEAN: Start with empty messages - title generates on first user message
        isLoading: false,
        parentId: sourceChatId,
      };

      // Update state in a controlled way
      setChatSessions(prevSessions => {
        const updatedSessions = [...prevSessions, newSession];
        
        // Calculate the new branch with the updated sessions
        const newBranch = getBranchForChat(newChatId, updatedSessions);
        console.log('🐛 Calculated new branch:', newBranch);
        
        // Update the visible chats and current index
        setVisibleChatIds(newBranch);
        const newChatIndex = newBranch.indexOf(newChatId);
        setCurrentChatIndex(newChatIndex !== -1 ? newChatIndex : newBranch.length - 1);
        
        console.log('🐛 Subchat creation completed:', {
          newChatId,
          branch: newBranch,
          focusIndex: newChatIndex
        });
        
        return updatedSessions;
      });
      
    } catch (error) {
      console.error('❌ Error creating subchat:', error);
      toast({
        title: 'Error',
        description: 'Failed to create subchat. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleSubmit = async (chatId: string, userInput: string) => {
    if (!userInput) return;
    
    console.log('🐛 handleSubmit called:', { 
      providedChatId: chatId, 
      userInput: userInput.substring(0, 50) + '...', 
      currentChatIndex, 
      visibleChatIds,
      totalSessions: chatSessions.length
    });
    
    // Determine the target chat ID - prefer the provided chatId over fallback
    const targetChatId = chatId || visibleChatIds[currentChatIndex];
    
    if (!targetChatId || targetChatId === 'undefined' || typeof targetChatId !== 'string') {
        console.error("❌ No valid chat ID found for message routing:", {
          providedChatId: chatId,
          fallbackChatId: visibleChatIds[currentChatIndex],
          currentChatIndex,
          visibleChatIds,
          allSessionIds: chatSessions.map(s => s.id)
        });
        toast({
          title: 'Error',
          description: 'Unable to send message. Please select a valid chat or create a new one.',
          variant: 'destructive',
        });
        return;
    }

    // Verify the target chat actually exists
    const targetSession = chatSessions.find(s => s.id === targetChatId);
    if (!targetSession) {
      console.error("❌ Target chat session not found:", {
        targetChatId,
        availableSessions: chatSessions.map(s => ({ id: s.id, title: s.title }))
      });
      toast({
        title: 'Error',
        description: 'Chat session not found. Please refresh and try again.',
        variant: 'destructive',
      });
      return;
    }

    console.log('✅ Routing message to:', { 
      targetChatId, 
      targetTitle: targetSession.title,
      isRoot: !targetSession.parentId 
    });

    // Add user message to the target chat
    setChatSessions((prev) =>
      prev.map((session) =>
        session.id === targetChatId
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
        const chatBeforeUpdate = chatSessions.find(c => c.id === targetChatId);
        const isFirstMessage = chatBeforeUpdate && chatBeforeUpdate.messages.length === 0;
        const isTemporaryId = targetChatId.startsWith('temp-');

        // Create a streaming assistant message
        const streamingMessageId = String(Date.now() + 1);
        const assistantMessage: Message = {
          id: streamingMessageId,
          role: 'assistant',
          content: '',
          sources: [],
          relatedTopics: [],
        };

        // Add empty assistant message to show streaming
        setChatSessions((prev) =>
          prev.map((session) =>
            session.id === targetChatId
              ? {
                  ...session,
                  messages: [...session.messages, assistantMessage],
                  isLoading: true,
                }
              : session
          )
        );

        let finalChatId = targetChatId;
        let streamingContent = '';

        // Handle new conversation creation if needed
        if (isTemporaryId) {
          const newConversation = await chatAPI.createConversation();
          finalChatId = newConversation.node_id;
          setChatSessions((prev) =>
            prev.map((session) =>
              session.id === targetChatId
                ? { ...session, id: finalChatId }
                : session
            )
          );
          setVisibleChatIds(prev => prev.map(id => id === targetChatId ? finalChatId : id));
        }

        // Stream the AI response using client-side API
        console.log('🐛 About to call sendMessageStream with finalChatId:', finalChatId);
        await chatAPI.sendMessageStream(
          finalChatId,
          userInput,
          // onChunk - append each chunk to the message
          (chunk: string) => {
            streamingContent += chunk;
            setChatSessions((prev) =>
              prev.map((session) =>
                session.id === finalChatId
                  ? {
                      ...session,
                      messages: session.messages.map((msg) =>
                        msg.id === streamingMessageId
                          ? { ...msg, content: streamingContent }
                          : msg
                      ),
                    }
                  : session
              )
            );
          },
          // onTitle - update title if generated
          (title: string) => {
            setChatSessions((prev) =>
              prev.map((session) =>
                session.id === finalChatId
                  ? { ...session, title }
                  : session
              )
            );
          },
          // onComplete - mark as finished
          () => {
            setChatSessions((prev) =>
              prev.map((session) =>
                session.id === finalChatId
                  ? { ...session, isLoading: false }
                  : session
              )
            );
          },
          // onError - handle errors
          (error: Error) => {
            console.error('Streaming error:', error);
            setChatSessions((prev) =>
              prev.map((session) =>
                session.id === finalChatId
                  ? { 
                      ...session, 
                      isLoading: false,
                      messages: session.messages.map((msg) =>
                        msg.id === streamingMessageId
                          ? { ...msg, content: 'Sorry, an error occurred while processing your request.' }
                          : msg
                      )
                    }
                  : session
              )
            );
            toast({
              variant: 'destructive',
              title: 'Error',
              description: 'Failed to get a response from the AI.',
            });
          }
        );

    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to get a response from the AI.',
      });
       setChatSessions((prev) =>
        prev.map((session) =>
          session.id === targetChatId ? { ...session, isLoading: false } : session
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
