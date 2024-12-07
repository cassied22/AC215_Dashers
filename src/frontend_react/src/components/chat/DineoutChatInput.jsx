'use client';
import React, { useState, useRef } from 'react';
import { Send, CameraAltOutlined, Restaurant } from '@mui/icons-material';
import IconButton from '@mui/material/IconButton';
import DineOutMap from './DineOutMap';

const DineoutChatInput = ({
    onSendMessage = () => { },
    initialMessage = '',
    placeholder = "Type your message..."
}) => {
    const [message, setMessage] = useState(initialMessage);
    const [selectedImage, setSelectedImage] = useState(null);
    const [showDineOutMap, setShowDineOutMap] = useState(false);
    const textAreaRef = useRef(null);
    const fileInputRef = useRef(null);

    const handleSubmit = () => {
        if (message.trim() || selectedImage) {
            console.log('Submitting message:', message);
            const newMessage = {
                text: message,
                image: selectedImage,
                timestamp: new Date(),
                dineoutLocation: showDineOutMap ? 'Enabled' : null
            };

            // Call the onSendMessage prop with the new message
            onSendMessage(newMessage);

            // Reset input fields
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
        <div className="bg-white/80 backdrop-blur-lg rounded-xl shadow-lg p-6 max-w-md mx-auto">
            {showDineOutMap && (
                <div className="mb-4">
                    <DineOutMap />
                </div>
            )}

            <div className="relative mb-4">
                <textarea
                    ref={textAreaRef}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    className="w-full p-2 border rounded-lg resize-none"
                    placeholder={placeholder}
                    rows={4}
                />
            </div>

            <div className="flex items-center justify-between">
                <div className="flex space-x-2">
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        onChange={handleImageUpload}
                        accept="image/*"
                    />
                    <IconButton
                        onClick={() => fileInputRef.current.click()}
                        className="text-gray-600 hover:bg-gray-100 rounded-lg"
                    >
                        <CameraAltOutlined />
                    </IconButton>
                    <IconButton
                        onClick={toggleDineOutMap}
                        color={showDineOutMap ? 'primary' : 'default'}
                        className="text-gray-600 hover:bg-gray-100 rounded-lg"
                    >
                        <Restaurant />
                    </IconButton>
                </div>
                <IconButton
                    onClick={handleSubmit}
                    disabled={!message.trim() && !selectedImage}
                    className="text-blue-600 hover:bg-blue-100 rounded-lg"
                >
                    <Send />
                </IconButton>
            </div>

            {selectedImage && (
                <div className="mt-2 text-sm text-gray-500">
                    Image selected: {selectedImage.name}
                </div>
            )}
        </div>
    );
};

export default DineoutChatInput;