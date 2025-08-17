
'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { InsightFlowIcon } from '@/components/icons';
import { Github, Key } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();

  const handleLogin = () => {
    // In a real app, you'd have authentication logic here.
    // For this prototype, we'll just navigate to the main chat page.
    router.push('/');
  };

  return (
    <main className="flex min-h-svh w-full items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-2xl">
          <CardHeader className="text-center">
            <div className="mb-4 flex justify-center">
              <InsightFlowIcon className="h-12 w-12" />
            </div>
            <CardTitle className="text-2xl">Welcome to InsightFlow</CardTitle>
            <CardDescription>Sign in to continue to the chatbot.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="m@example.com" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" required />
              </div>
              <Button onClick={handleLogin} className="w-full">
                Login with Email
              </Button>
            </div>
            <div className="my-6 flex items-center">
              <div className="flex-grow border-t border-muted" />
              <span className="mx-4 text-sm text-muted-foreground">OR</span>
              <div className="flex-grow border-t border-muted" />
            </div>
            <div className="space-y-4">
                <Button variant="outline" className="w-full">
                    <Github className="mr-2" />
                    Login with GitHub
                </Button>
                <Button variant="outline" className="w-full">
                    <Key className="mr-2" />
                    Continue with SSO
                </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
