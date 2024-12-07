'use client';

import React, { useState } from 'react';
import DineOutMap from '@/components/chat/DineOutMap';

export default function DineoutChatTest() {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);

    const handleSubmit = async () => {
        if (message.trim()) {
            try {
                // Call the API route
                const response = await fetch(`/api/places?keyword=${message}`);
                const data = await response.json();

                if (data.results) {
                    const newMessages = data.results.map((place) => ({
                        text: `Found: ${place.name} at ${place.vicinity}`,
                        dineoutLocation: place.geometry.location,
                    }));

                    setMessages((prevMessages) => [...prevMessages, ...newMessages]);
                }

                setMessage('');
            } catch (error) {
                console.error('Error fetching restaurant data:', error);
            }
        }
    };

    return (
        <div className="dineout-chat-container">
            <h1>🍴 Daily Food Assistant</h1>
            <div style={{ height: '400px', marginBottom: '1rem' }}>
                <DineOutMap
                    locations={messages
                        .filter((msg) => msg.dineoutLocation)
                        .map((msg) => msg.dineoutLocation)}
                />
            </div>
            <div className="chat-input">
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your query, e.g., 'Pizza' or 'Chinese food'"
                />
                <button onClick={handleSubmit}>Search</button>
            </div>
            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <p key={index}>{msg.text}</p>
                ))}
            </div>
        </div>
    );
}
