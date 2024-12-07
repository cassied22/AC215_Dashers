'use client';
import React, { useState } from 'react';
import { Send, CameraAltOutlined, Restaurant } from '@mui/icons-material';
import IconButton from '@mui/material/IconButton';
import DineOutMap from '../../components/chat/DineOutMap';

export default function DineoutChatTest() {
    const [message, setMessage] = useState('');
    const [selectedImage, setSelectedImage] = useState(null);
    const [showDineOutMap, setShowDineOutMap] = useState(false);
    const [messages, setMessages] = useState([]);

    const handleSubmit = () => {
        if (message.trim() || selectedImage) {
            const newMessage = {
                text: message,
                image: selectedImage,
                timestamp: new Date(),
                dineoutLocation: showDineOutMap
            };

            // Add message to list
            setMessages(prevMessages => [...prevMessages, newMessage]);

            // Reset fields
            setMessage('');
            setSelectedImage(null);
            setShowDineOutMap(false);
        }
    };

    const toggleDineOutMap = () => {
        setShowDineOutMap(!showDineOutMap);
    };

    const handleImageUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedImage(file);
        }
    };

    return (
        <div className="container mx-auto p-6 max-w-2xl">
            <h1 className="text-2xl font-bold mb-6 text-center">Dine Out</h1>

            {/* Dineout Map Section */}
            {showDineOutMap && (
                <div className="mb-4">
                    <DineOutMap />
                </div>
            )}

            {/* Chat Input Area */}
            <div className="bg-white border rounded-lg p-4 shadow-md">
                <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    className="w-full p-2 border rounded-lg mb-4"
                    placeholder="Type your message..."
                    rows={4}
                />

                <div className="flex justify-between items-center">
                    <div className="flex space-x-2">
                        <input
                            type="file"
                            className="hidden"
                            id="image-upload"
                            onChange={handleImageUpload}
                            accept="image/*"
                        />
                        <IconButton
                            onClick={() => document.getElementById('image-upload').click()}
                            className="text-gray-600 hover:bg-gray-100"
                        >
                            <CameraAltOutlined />
                        </IconButton>
                        <IconButton
                            onClick={toggleDineOutMap}
                            color={showDineOutMap ? 'primary' : 'default'}
                            className="text-gray-600 hover:bg-gray-100"
                        >
                            <Restaurant />
                        </IconButton>
                    </div>
                    <IconButton
                        onClick={handleSubmit}
                        disabled={!message.trim() && !selectedImage}
                        className="text-blue-600 hover:bg-blue-100"
                    >
                        <Send />
                    </IconButton>
                </div>

                {/* Image Preview */}
                {selectedImage && (
                    <div className="mt-2 text-sm text-gray-500">
                        Selected Image: {selectedImage.name}
                    </div>
                )}
            </div>
        </div>
    );
}