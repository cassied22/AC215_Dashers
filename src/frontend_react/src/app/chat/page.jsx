'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import ChatInput from '@/components/chat/ChatInput';
import ChatHistory from '@/components/chat/ChatHistory';
import ChatHistorySidebar from '@/components/chat/ChatHistorySidebar';
import ChatMessage from '@/components/chat/ChatMessage';
import DataService from "../../services/DataService";
import { uuid } from "../../services/Common";

export default function ChatPage() {
    // Extract the query parameters
    const searchParams = useSearchParams();
    const ingredient = searchParams.get('ingredient'); // Extract the ingredient from the URL
    const model = searchParams.get('model'); // || 'llm';
    const chat_id = searchParams.get('id'); 
    console.log(chat_id, model);

    // Component States
    const [chat, setChat] = useState(null);
    const [hasActiveChat, setHasActiveChat] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const [selectedModel, setSelectedModel] = useState(model);
    const router = useRouter();
    const [currentFoodTitle, setCurrentFoodTitle] = useState(null);

    const fetchChat = async (id) => {
        try {
            setChat(null);
            const response = await DataService.GetChat(model, id);
            setChat(response.data);
            setCurrentFoodTitle(response.data?.title || ""); // Update title
            console.log(chat);
        } catch (error) {
            console.error('Error fetching chat:', error);
            setChat(null);
        }
    };
    useEffect(() => {
        if (chat_id) {
            fetchChat(chat_id);
            setHasActiveChat(true);
        } else {
            setChat(null);
            setHasActiveChat(false);
        }
    }, [chat_id]);

    // Function to start a new chat
    const startChatWithIngredient = async (message) => {
        console.log('Sending message:', message, 'to model:', model);
        try {
            setIsTyping(true);
            setHasActiveChat(false);

            // Set initial message with a unique message ID
            message["message_id"] = uuid();
            message["role"] = 'user';
            setChat({ messages: [message] });  // Display the user's input initially

            // Submit chat to start the conversation
            const response = await DataService.StartChatWithLLM(model, message);
            setCurrentFoodTitle(response.title || ""); // Update title
            setIsTyping(false);
            setChat(response.data);
            setHasActiveChat(true);
            router.push('/chat?model=' + selectedModel + '&id=' + response.data["chat_id"]);
        } catch (error) {
            console.error('Error fetching chat:', error);
            setIsTyping(false);
            setChat(null);
            setHasActiveChat(false);
            router.push('/chat?model=' + selectedModel);
        }
    };
    const appendChat = (message) => {
        console.log('Sending message:', message, 'to model:', model);
        if (!chat?.chat_id) {
            console.error('No active chat session found. Start a chat first.');
            return;
        }
    
        const chat_id = chat.chat_id; // Extract chat_id from the chat state
    
        const continueChat = async (id, message) => {
            try {
                // Show typing indicator
                setIsTyping(true);
    
                // Add the user's message temporarily to the chat
                const tempMessages = [...chat.messages, { ...message, role: 'user', message_id: uuid() }];
                setChat({ ...chat, messages: tempMessages });
    
                // Submit chat to the server
                const response = await DataService.ContinueChatWithLLM(model, id, message);

                const newTitle = response.data?.title || chat.title || "Untitled Conversation";
                setCurrentFoodTitle(newTitle); // Update the title state
    
                // Update the chat state with the server response
                setChat(response.data);
    
                // Hide typing indicator
                setIsTyping(false);
            } catch (error) {
                console.error('Error appending chat:', error);
                setIsTyping(false);
            }
        };
    
        continueChat(chat_id, message);
    }; 
    // Force re-render by updating the key
    const forceRefresh = () => {
        setRefreshKey(prevKey => prevKey + 1);
    };
    const handleModelChange = (newValue) => {

        setSelectedModel(newValue);
        var path = '/chat?model=' + newValue;
        if (chat_id) {
            path = path + '&id=' + chat_id;
        }
        router.push(path)
    };

    // Use Effect to start the conversation if an ingredient is provided
    useEffect(() => {
        if (ingredient) {
            // If there is an ingredient, start the conversation using it
            startChatWithIngredient({ content: ingredient });
        }
    }, [ingredient]);

    return (
        <div className="h-screen flex flex-col pt-0">
            {!hasActiveChat ? (
                <div className="flex h-[calc(100vh-64px)] pt-0">
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
                                onModelChange={handleModelChange}
                                disableModelSelect={false}
                                currentFoodTitle={currentFoodTitle} // Pass the current title
                            />
                        </div>
                    </div>
                </div>
            ) : (
                <div className="flex h-[calc(100vh-64px)] pt-0">
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
                                onSendMessage={appendChat}
                                chat={chat}
                                selectedModel={selectedModel}
                                onModelChange={handleModelChange}
                                disableModelSelect={false}
                                currentFoodTitle={currentFoodTitle} // Pass the current title
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
