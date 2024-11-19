'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import ChatInput from '@/components/chat/ChatInput';
import ChatHistorySidebar from '@/components/chat/ChatHistorySidebar';
import ChatMessage from '@/components/chat/ChatMessage';
import DataService from "../../services/DataService";
import { uuid } from "../../services/Common";

export default function ChatPage() {
    // Extract the query parameters
    const searchParams = useSearchParams();
    const ingredient = searchParams.get('ingredient'); // Extract the ingredient from the URL
    const model = searchParams.get('model') || 'llm';

    // Component States
    const [chat, setChat] = useState(null);
    const [hasActiveChat, setHasActiveChat] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const [selectedModel, setSelectedModel] = useState(model);
    const router = useRouter();

    // Function to start a new chat
    const startChatWithIngredient = async (message) => {
        try {
            setIsTyping(true);
            setHasActiveChat(true);

            // Set initial message with a unique message ID
            message["message_id"] = uuid();
            message["role"] = 'user';
            setChat({ messages: [message] });  // Display the user's input initially

            // Submit chat to start the conversation
            const response = await DataService.StartChatWithLLM(model, message);
            setIsTyping(false);
            setChat(response.data);
            router.push('/chat?model=' + selectedModel + '&id=' + response.data["chat_id"]);
        } catch (error) {
            console.error('Error fetching chat:', error);
            setIsTyping(false);
            setChat(null);
            setHasActiveChat(false);
            router.push('/chat?model=' + selectedModel);
        }
    };

    // Use Effect to start the conversation if an ingredient is provided
    useEffect(() => {
        if (ingredient) {
            // If there is an ingredient, start the conversation using it
            startChatWithIngredient({ content: ingredient });
        }
    }, [ingredient]);

    return (
        <div className="h-screen flex flex-col pt-16">
            {!hasActiveChat ? (
                <>
                    {/* Hero Section */}
                    <section className="flex-shrink-0 min-h-[400px] flex items-center justify-center bg-gradient-to-br from-purple-100 via-pink-50 to-orange-50">
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 via-pink-500/10 to-orange-400/10" />
                        <div className="container mx-auto px-4 max-w-3xl relative z-10 pt-20">
                            <div className="text-center">
                                <h1 className="text-4xl md:text-6xl font-bold gradient-text mb-6">
                                    Upload an image here
                                </h1>
                                <div className="bg-white/80 backdrop-blur-lg rounded-xl shadow-lg p-6">
                                    <ChatInput
                                        onSendMessage={startChatWithIngredient}
                                        selectedModel={selectedModel}
                                        onModelChange={setSelectedModel}
                                    />
                                </div>
                            </div>
                        </div>
                    </section>
                </>
            ) : (
                <div className="flex h-[calc(100vh-64px)]">
                    {/* Sidebar */}
                    <div className="w-80 flex-shrink-0 bg-white border-r border-gray-200">
                        <ChatHistorySidebar chat_id={chat?.chat_id} model={model} />
                    </div>

                    {/* Main Chat Area */}
                    <div className="flex-1 flex flex-col h-full overflow-hidden">
                        <div className="flex-1 overflow-y-auto">
                            <ChatMessage
                                chat={chat}
                                isTyping={isTyping}
                                model={model}
                            />
                        </div>
                        <div className="flex-shrink-0 border-t border-gray-200 bg-white">
                            <ChatInput
                                onSendMessage={startChatWithIngredient}
                                chat={chat}
                                selectedModel={selectedModel}
                                onModelChange={setSelectedModel}
                                disableModelSelect={true}
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
