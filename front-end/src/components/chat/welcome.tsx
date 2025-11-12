
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { InsightFlowIcon } from '../icons';
import { BrainCircuit, BookOpen, Search, DraftingCompass } from 'lucide-react';

interface WelcomeProps {
  onExampleClick: (example: string) => void;
}

const examplePrompts = [
    {
        icon: <BrainCircuit className="h-8 w-8 text-primary" />,
        title: 'Brainstorm ideas',
        prompt: 'Brainstorm ideas for a new marketing campaign for a local coffee shop.',
        description: 'for a new marketing campaign'
    },
    {
        icon: <BookOpen className="h-8 w-8 text-primary" />,
        title: 'Summarize a topic',
        prompt: 'Summarize the key concepts of quantum computing in simple terms.',
        description: 'on quantum computing'
    },
    {
        icon: <Search className="h-8 w-8 text-primary" />,
        title: 'Compare and contrast',
        prompt: 'Compare and contrast the pros and cons of Next.js and React for web development.',
        description: 'Next.js vs. React'
    },
    {
        icon: <DraftingCompass className="h-8 w-8 text-primary" />,
        title: 'Design a plan',
        prompt: 'Design a 5-day itinerary for a cultural trip to Kyoto, Japan.',
        description: 'for a trip to Kyoto'
    },
];

export function Welcome({ onExampleClick }: WelcomeProps) {
  return (
    <div className="flex h-full w-full flex-col items-center justify-center p-4">
      <div className="flex flex-col items-center text-center mb-12">
        <div className="mb-4 flex items-center gap-3">
          <InsightFlowIcon className="h-12 w-12" />
        </div>
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">Welcome to InsightFlow</h1>
        <p className="mt-4 text-lg text-muted-foreground max-w-xl">
          Your intelligent partner in discovery. How can I assist you today?
        </p>
      </div>
      <div className="w-full max-w-4xl grid grid-cols-1 gap-4 sm:grid-cols-2">
        {examplePrompts.map((item, index) => (
          <Card
            key={index}
            className="cursor-pointer transition-transform duration-200 hover:scale-[1.02] hover:bg-secondary/50"
            onClick={() => onExampleClick(item.prompt)}
          >
            <CardHeader>
                <div className='flex items-center gap-4'>
                    {item.icon}
                    <div className='flex flex-col'>
                        <CardTitle className="text-lg">{item.title}</CardTitle>
                        <CardDescription>{item.description}</CardDescription>
                    </div>
                </div>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  );
}
