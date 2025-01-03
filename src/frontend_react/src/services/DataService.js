import { BASE_API_URL, uuid } from "./Common";
import { mockChats } from "./SampleData";
import axios from 'axios';

console.log("BASE_API_URL:", BASE_API_URL)

// Create an axios instance with base configuration
const api = axios.create({
    baseURL: BASE_API_URL
});

// Add request interceptor to include session ID in headers
api.interceptors.request.use((config) => {
    const sessionId = localStorage.getItem('userSessionId');
    if (sessionId) {
        config.headers['X-Session-ID'] = sessionId;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

const DataService ={

    Init: function(){
        // any initializatino logic
    },
    ImageClassificationPredict: async function(message){
        return await api.post("/llm-food-detection/chats", message)
        // console.log(`Final URL: ${BASE_API_URL}/llm-food-detection/chats`);
        // return await axios.post(`/llm-food-detection/chats`, message)
    },

    GetChats: async function (model, limit) {
        return await api.get("/" + model + "/chats?limit=" + limit);
    },
    GetChat: async function (model, chat_id) {
        return await api.get("/" + model + "/chats/" + chat_id);
    },

    StartChatWithLLM: async function (model, message) {
        return await api.post(`/${model}/chats`, message);
    },
    ContinueChatWithLLM: async function (model, chat_id, message) {
        return await api.post("/" + model + "/chats/" + chat_id, message);
    },

    SearchYouTube: async function (recipe_name) {
        try {
            const response = await api.get("/youtube/", {
                params: { recipe_name },
            });
            console.log("API Response:", response.data);
            return response.data;
        } catch (error) {
            console.error("API Error:", error.message, error.response?.data);
            throw error;
        }
    },
    
    
    // ImageClassificationPredict: async function (formData) {
    //     // Simulate API delay
    //     await new Promise(resolve => setTimeout(resolve, 1500));

    //     // Mock response data
    //     const mockResults = {
    //         success: true,
    //         model: "MockNet v1.0",
    //         timestamp: new Date().toISOString(),
    //         results: [
    //             {
    //                 class_index: 1,
    //                 class_name: "Broccoli"
    //             },
    //             {
    //                 class_index: 2,
    //                 class_name: "Chicken"
    //             },
    //             {
    //                 class_index: 3,
    //                 class_name: "Cheese"
    //             }
    //         ],
    //         processing_time: "0.845 seconds",
    //         image_size: "800x600",
    //         format: "jpeg"
    //     };

    //     // Randomly fail sometimes to test error handling (10% chance)
    //     if (Math.random() < 0.1) {
    //         throw new Error('Mock classification failed');
    //     }

    //     return Promise.resolve({ data: mockResults });
    // },
    // Audio2Text: async function (formData) {
    //     // Simulate API delay
    //     await new Promise(resolve => setTimeout(resolve, 2000));

    //     // Mock response data
    //     const mockResults = [
    //         {
    //             transcript: "Hello, this is a test recording of the audio to text conversion system.",
    //             confidence: 0.95
    //         },
    //         {
    //             transcript: "The quick brown fox jumps over the lazy dog.",
    //             confidence: 0.88
    //         },
    //         {
    //             transcript: "This is an example of automated speech recognition.",
    //             confidence: 0.92
    //         }
    //     ];

    //     // Randomly fail sometimes (10% chance)
    //     if (Math.random() < 0.1) {
    //         throw new Error('Mock transcription failed');
    //     }

    //     return Promise.resolve({ data: mockResults });
    // },
    // Text2Audio: async function (data) {
    //     // Simulate API delay
    //     await new Promise(resolve => setTimeout(resolve, 1500));

    //     // Mock response data
    //     const mockResults = {
    //         success: true,
    //         data: {
    //             text: data.text,
    //             audio_path: `mock_audio_${Date.now()}.mp3`,
    //             duration: "2.5s",
    //             format: "mp3",
    //             timestamp: new Date().toISOString()
    //         }
    //     };

    //     // Randomly fail sometimes (10% chance)
    //     if (Math.random() < 0.1) {
    //         throw new Error('Text to speech conversion failed');
    //     }

    //     return Promise.resolve({ data: mockResults });
    // },

    // Text2AudioGetAudio: function (audioPath) {
    //     // For testing, return a sample audio URL
    //     return 'https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav';
    // },

    // StyleTransferGetContentImages: async function () {
    //     // Mock content images
    //     return {
    //         data: Array.from({ length: 12 }, (_, i) => `content-${i + 1}`)
    //     };
    // },
    // StyleTransferGetStyleImages: async function () {
    //     // Mock style images
    //     return {
    //         data: Array.from({ length: 12 }, (_, i) => `style-${i + 1}`)
    //     };
    // },
    // StyleTransferApplyStyleTransfer: async function (styleImage, contentImage) {
    //     // Simulate API delay
    //     await new Promise(resolve => setTimeout(resolve, 2000));

    //     return {
    //         data: {
    //             stylized_image: 'result-image',
    //             style_image: styleImage,
    //             content_image: contentImage,
    //             processing_time: '2.5s'
    //         }
    //     };
    // },
    // StyleTransferGetImage: function (imagePath) {
    //     // For testing, return a placeholder image
    //     return `https://picsum.photos/400/400?random=${imagePath}`;
    // },

    // GetChats: async function (model, limit) {
    //     // Simulate API delay
    //     await new Promise(resolve => setTimeout(resolve, 500));

    //     const limitedChats = mockChats.slice(0, limit || mockChats.length);
    //     return Promise.resolve({ data: limitedChats });
    // },
    // GetChat: async function (model, chat_id) {
    //     // Simulate API delay
    //     await new Promise(resolve => setTimeout(resolve, 300));

    //     const chat = mockChats.find(c => c.chat_id === chat_id);
    //     if (!chat) {
    //         throw new Error('Chat not found');
    //     }
    //     return Promise.resolve({ data: chat });
    // },

    // StartChatWithLLM: async function (model, message) {
    //     await new Promise(resolve => setTimeout(resolve, 1000));

    //     const newChat = {
    //         chat_id: uuid(),
    //         title: message.content.slice(0, 20) + "...",
    //         dts: Date.now(),
    //         messages: [
    //             {
    //                 message_id: uuid(),
    //                 role: "user",
    //                 content: message.content,
    //                 image_path: message.image_path
    //             },
    //             {
    //                 message_id: uuid(),
    //                 role: "assistant",
    //                 content: `Mock response to: ${message.content}`
    //             }
    //         ]
    //     };

    //     mockChats.unshift(newChat);
    //     return Promise.resolve({ data: newChat });
    // },
    // ContinueChatWithLLM: async function (model, chat_id, message) {
    //     await new Promise(resolve => setTimeout(resolve, 1000));

    //     const chat = mockChats.find(c => c.chat_id === chat_id);
    //     if (!chat) {
    //         throw new Error('Chat not found');
    //     }

    //     const newMessages = [
    //         {
    //             message_id: uuid(),
    //             role: "user",
    //             content: message.content,
    //             image_path: message.image_path
    //         },
    //         {
    //             message_id: uuid(),
    //             role: "assistant",
    //             content: `Mock response to: ${message.content}`
    //         }
    //     ];

    //     chat.messages.push(...newMessages);
    //     return Promise.resolve({ data: chat });
    // },
    // GetChatMessageImage: function (model, image_path) {
    //     // For testing, return a placeholder image
    //     return `https://picsum.photos/800/600?random=${encodeURIComponent(image_path)}`;
    // },
}

export default DataService;