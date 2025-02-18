import React from 'react';
import { Message, MessageType } from './types';
import { cn } from '@/lib/utils';
import { StreamingText } from '../ui/streaming-text';

interface MessagesListProps {
  messages: Message[];
  className?: string;
}

export function MessagesList({ messages, className }: MessagesListProps) {
  return (
    <div className={cn("space-y-4", className)}>
      {messages.map((message) => (
        <div
          key={message.id}
          className={`p-4 rounded-lg ${
            message.type === MessageType.USER
              ? "bg-muted"
              : message.status === "error"
              ? "bg-destructive/10 text-destructive"
              : message.status === "success"
              ? "bg-green-100 text-green-800 dark:bg-green-900/10 dark:text-green-400"
              : "bg-primary/10"
          }`}
        >
          {/* Avatar/Icon */}
          <div className="mt-1">
            {message.type === MessageType.USER ? (
              <span className="text-xl">👤</span>
            ) : (
              <span className="text-xl">🤖</span>
            )}
          </div>

          {/* Message Content */}
          <div className="flex-1">
            {Array.isArray(message.content) ? (
              <ul className="list-disc list-inside space-y-1">
                {message.content.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            ) : (
              <div className={cn(
                message.type === MessageType.USER && "text-gray-700",
                message.type === MessageType.SYSTEM && message.status === 'processing' && "text-blue-700",
                message.type === MessageType.SYSTEM && message.status === 'success' && "text-green-700",
                message.type === MessageType.SYSTEM && message.status === 'error' && "text-red-700"
              )}>
                <StreamingText
                  text={message.content as string}
                  delay={30}
                  showCursor={message.type === MessageType.SYSTEM}
                  playSound={message.type === MessageType.SYSTEM}
                />
              </div>
            )}
          </div>

          {/* Timestamp */}
          <p className="text-xs text-muted-foreground mt-2">
            {message.timestamp.toLocaleTimeString()}
          </p>
        </div>
      ))}
    </div>
  );
}

interface ProcessingStepsProps {
  steps: string[];
}

function ProcessingSteps({ steps }: ProcessingStepsProps) {
  const [currentStep, setCurrentStep] = React.useState(0);

  return (
    <div className="space-y-2">
      {steps.map((step, index) => (
        <div
          key={index}
          className={cn(
            "transition-opacity duration-200",
            index > currentStep && "opacity-0",
            index === currentStep && "text-blue-700",
            index < currentStep && "text-gray-500 opacity-60"
          )}
        >
          {index <= currentStep && (
            <div className="flex items-start gap-2">
              <span className="mt-1">💭</span>
              {index === currentStep ? (
                <StreamingText
                  text={step}
                  delay={30}
                  showCursor={true}
                  onComplete={() => {
                    if (currentStep < steps.length - 1) {
                      setCurrentStep(prev => prev + 1);
                    }
                  }}
                />
              ) : (
                <span>{step}</span>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
} 