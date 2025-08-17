
'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  Plus,
  MessageSquare,
  Search,
  ChevronLeft,
  User as UserIcon,
  Gem,
  SlidersHorizontal,
  Settings,
  HelpCircle,
  LogOut,
  FileText,
  Shield,
  Download,
  Keyboard,
  MoreHorizontal,
  Share,
  Pencil,
  Archive,
  Trash2,
} from 'lucide-react';
import { InsightFlowIcon } from './icons';
import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Input } from './ui/input';
import type { ChatSession } from '@/lib/types';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuGroup,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuPortal,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ScrollArea } from './ui/scroll-area';

interface SidebarProps {
  isSidebarOpen: boolean;
  setIsSidebarOpen: (isOpen: boolean) => void;
  className?: string;
  onNewChat: () => void;
  chatHistory: ChatSession[];
  activeChatId: string | null;
  setActiveChatId: (id: string) => void;
  onDeleteChat: (id: string) => void;
  onRenameChat: (id: string, newTitle: string) => void;
}

type ChatTreeItem = ChatSession & { children: ChatTreeItem[] };

export function Sidebar({
  isSidebarOpen,
  setIsSidebarOpen,
  className,
  onNewChat,
  chatHistory,
  activeChatId,
  setActiveChatId,
  onDeleteChat,
  onRenameChat,
}: SidebarProps) {
  const router = useRouter();

  const handleLogout = () => {
    // In a real app, you'd handle clearing auth state here.
    router.push('/login');
  };

  const handleRename = (chatId: string) => {
    const newTitle = window.prompt('Enter new chat title:');
    if (newTitle) {
      onRenameChat(chatId, newTitle);
    }
  };

  const filteredChatHistory = React.useMemo(() => {
    const chatMap = new Map<string, ChatTreeItem>();
    chatHistory.forEach(chat => {
      chatMap.set(chat.id, { ...chat, children: [] });
    });

    const chatTree: ChatTreeItem[] = [];
    chatMap.forEach(chat => {
      if (chat.parentId && chatMap.has(chat.parentId)) {
        chatMap.get(chat.parentId)!.children.push(chat);
      } else {
        chatTree.push(chat);
      }
    });

    return chatTree;
  }, [chatHistory]);
  
  const renderChatTree = (tree: ChatTreeItem[], isChild = false) => {
    return tree.map(chat => (
        <div key={chat.id} className={cn(isChild && 'ml-4 mt-1 space-y-1 border-l border-muted-foreground/20 pl-2', 'group/chat-item')}>
            <div className="flex items-center">
              <Button
                variant={activeChatId === chat.id ? 'secondary' : 'ghost'}
                className="w-full truncate justify-start text-sm h-9 flex-1"
                size={isSidebarOpen ? 'default' : 'icon'}
                onClick={() => setActiveChatId(chat.id)}
              >
                <MessageSquare className={cn('h-4 w-4 shrink-0', isSidebarOpen && 'mr-2')} />
                <span className={cn('truncate', !isSidebarOpen && 'hidden')}>
                  {chat.title}
                </span>
              </Button>
              {isSidebarOpen && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0 opacity-0 group-hover/chat-item:opacity-100 transition-opacity">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuItem><Share className="mr-2 h-4 w-4"/>Share</DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleRename(chat.id)}><Pencil className="mr-2 h-4 w-4"/>Rename</DropdownMenuItem>
                    <DropdownMenuItem><Archive className="mr-2 h-4 w-4"/>Archive</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-red-500 focus:text-red-500" onClick={() => onDeleteChat(chat.id)}>
                      <Trash2 className="mr-2 h-4 w-4"/>Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>
            {isSidebarOpen && chat.children.length > 0 && renderChatTree(chat.children, true)}
        </div>
    ));
  }


  return (
    <aside
      className={cn(
        'group/sidebar flex h-full flex-col border-r bg-sidebar-background text-sidebar-foreground transition-all duration-300 ease-in-out',
        isSidebarOpen ? 'w-72 p-4' : 'w-[72px] p-2 items-center',
        className
      )}
    >
      <div
        className={cn(
          'flex w-full items-center',
          !isSidebarOpen && 'justify-center'
        )}
      >
        <InsightFlowIcon className="h-8 w-8 shrink-0" />
        <h1
          className={cn(
            'ml-2 text-xl font-semibold tracking-tighter whitespace-nowrap',
            !isSidebarOpen && 'hidden'
          )}
        >
          InsightFlow
        </h1>
      </div>

      <Button
        onClick={onNewChat}
        className={cn('mt-6 mb-4 w-full h-10', !isSidebarOpen && 'justify-center')}
        variant="default"
        size={isSidebarOpen ? 'default' : 'icon'}
      >
        <Plus className={cn(isSidebarOpen && 'mr-2', 'h-5 w-5')} />
        <span className={cn(isSidebarOpen ? 'inline' : 'sr-only')}>New Chat</span>
      </Button>

      <div className={cn('relative mb-2', !isSidebarOpen && 'hidden')}>
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search chat..."
          className="pl-9 bg-sidebar-accent border-sidebar-border focus:ring-sidebar-ring h-9"
        />
      </div>

      <ScrollArea className={cn('flex-1 min-h-0', isSidebarOpen && '-mr-4 pr-4')}>
        <h2
          className={cn(
            'mb-2 mt-2 text-sm font-semibold tracking-tight text-muted-foreground',
            !isSidebarOpen && 'hidden'
          )}
        >
          Chat History
        </h2>
        <div className={cn('space-y-1')}>
          {renderChatTree(filteredChatHistory)}
        </div>
      </ScrollArea>

      <div className="mt-auto flex w-full flex-col pt-4 space-y-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <div
              className={cn(
                'w-full h-auto justify-center py-2 cursor-pointer rounded-md hover:bg-sidebar-accent/80',
                isSidebarOpen ? 'px-2' : 'px-0'
              )}
            >
              <div className={cn('flex w-full items-center gap-2', !isSidebarOpen && 'justify-center')}>
                <Avatar className="h-8 w-8 shrink-0">
                  <AvatarImage src="https://placehold.co/40x40.png" alt="N" data-ai-hint="profile avatar" />
                  <AvatarFallback>KS</AvatarFallback>
                </Avatar>
                <div className={cn('flex flex-col items-start', !isSidebarOpen && 'hidden')}>
                  <span className="font-semibold whitespace-nowrap text-sm">
                    Kabbo Sarker
                  </span>
                  <span className="text-xs text-muted-foreground">Free</span>
                </div>
              </div>
            </div>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-64 mb-2 ml-2" side="top" align="start">
            <DropdownMenuItem>
              <UserIcon />
              sarkarkabbo72@gmail.com
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem>
                <Gem />
                Upgrade plan
              </DropdownMenuItem>
              <DropdownMenuItem>
                <SlidersHorizontal />
                Customize ChatGPT
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings />
                Settings
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>
                <HelpCircle />
                Help
              </DropdownMenuSubTrigger>
              <DropdownMenuPortal>
                <DropdownMenuSubContent className="w-56">
                  <DropdownMenuItem>
                    <HelpCircle />
                    Help center
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <FileText />
                    Release notes
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Shield />
                    Terms & policies
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Download />
                    Download apps
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Keyboard />
                    Keyboard shortcuts
                  </DropdownMenuItem>
                </DropdownMenuSubContent>
              </DropdownMenuPortal>
            </DropdownMenuSub>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout}>
              <LogOut />
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button
          variant="ghost"
          size="default"
          className="w-full h-10 bg-transparent hover:bg-sidebar-accent/80"
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        >
          <ChevronLeft className={cn('h-5 w-5 shrink-0 transition-transform', !isSidebarOpen && 'rotate-180')} />
        </Button>
      </div>
    </aside>
  );
}
