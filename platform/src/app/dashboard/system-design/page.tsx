'use client'

import { useEffect } from 'react'
import { VideoBox } from '@/components/VideoBox'
import { useTavusConversation } from '@/hooks/useTavusConversation'
import { getSystemDesignContext } from '@/lib/conversation-context'

export default function SystemDesignPage() {
    const { conversationState, startConversation } = useTavusConversation()

    // Initialize Tavus conversation on page load
    useEffect(() => {
        // Temporarily disabled
        /*
        const initializeTavusConversation = async () => {
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
            }
        }

        initializeTavusConversation()
        */
    }, [startConversation])

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-light text-foreground">System Design Interview</h1>
                <p className="text-muted-foreground mt-1">
                    Collaborate on the system design diagram below.
                </p>
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
