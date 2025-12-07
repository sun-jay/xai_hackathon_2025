'use client'

import { useState } from 'react'
import { VideoBox } from '@/components/VideoBox'
import { useTavusConversation } from '@/hooks/useTavusConversation'
import { getSystemDesignContext } from '@/lib/conversation-context'

export default function SystemDesignPage() {
    const { conversationState, startConversation, endConversation } = useTavusConversation()
    const [isStarting, setIsStarting] = useState(false)
    const [isEnding, setIsEnding] = useState(false)

    const handleStartCall = async () => {
        setIsStarting(true)
        try {
            const conversationalContext = getSystemDesignContext()

            const conversationConfig = {
                replica_id: process.env.NEXT_PUBLIC_TAVUS_REPLICA_ID || '',
                persona_id: process.env.NEXT_PUBLIC_TAVUS_PERSONA_ID || '',
                conversational_context: conversationalContext,
                custom_greeting: "Hi I am your Grok interviewer, I will be conducting your system design interview today."
            }

            console.log('🚀 Starting Tavus conversation with config:', conversationConfig)

            await startConversation(conversationConfig)
        } catch (error) {
            console.error('Failed to initialize Tavus conversation:', error)
        } finally {
            setIsStarting(false)
        }
    }

    const handleEndCall = async () => {
        setIsEnding(true)
        try {
            console.log('🔚 Ending Tavus conversation')
            await endConversation()
        } catch (error) {
            console.error('Failed to end Tavus conversation:', error)
        } finally {
            setIsEnding(false)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-light text-foreground">System Design Interview</h1>
                    <p className="text-muted-foreground mt-1">
                        Collaborate on the system design diagram below.
                    </p>
                </div>

                <div className="flex gap-2">
                    {!conversationState.conversationUrl && (
                        <button
                            onClick={handleStartCall}
                            disabled={isStarting || conversationState.status === 'loading'}
                            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isStarting || conversationState.status === 'loading' ? 'Starting...' : 'Start Call'}
                        </button>
                    )}

                    {conversationState.conversationUrl && (
                        <button
                            onClick={handleEndCall}
                            disabled={isEnding}
                            className="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isEnding ? 'Ending...' : 'End Call'}
                        </button>
                    )}
                </div>
            </div>

            <VideoBox
                conversationUrl={conversationState.conversationUrl}
                isLoading={conversationState.status === 'loading'}
            />

            <div className="w-full h-[800px] border border-border rounded-xl overflow-hidden shadow-sm bg-card">
                <iframe
                    src="http://localhost:3010"
                    className="w-full h-full block"
                    title="Excalidraw Canvas"
                />
            </div>
        </div>
    )
}
