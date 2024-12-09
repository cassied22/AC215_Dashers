'use client'

import { useRef, useState } from 'react';
import {
    CloudUpload,
    CameraAlt
} from '@mui/icons-material';
import DataService from '@/services/DataService';
import { useRouter } from 'next/navigation';


export default function ImageClassification() {
    // Component States
    const inputFile = useRef(null);
    const [image, setImage] = useState(null);
    const [prediction, setPrediction] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const router = useRouter();

    // Handlers
    const handleImageUploadClick = () => {
        inputFile.current.click();
    };

    const handleOnChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;
    
        // Set loading state to true as processing starts
        setIsLoading(true);
    
        try {
            // Update the UI with image preview
            setImage(URL.createObjectURL(file));
    
            // Convert the file to Base64
            const reader = new FileReader();
            reader.readAsDataURL(file);
    
            reader.onload = async () => {
                try {
                    // Extract the Base64 content from the reader result
                    const base64String = reader.result.split(',')[1]; // Extracting only the Base64 part
    
                    // Prepare the payload for the API request
                    const payload = {
                        content: 'user upload',
                        image: `data:image/jpeg;base64,${base64String}`,
                    };
    
                    // Send request to the API
                    const response = await DataService.ImageClassificationPredict(payload);
    
                    // Transform API response to match mock format
                    const apiMessages = response.data.messages;
                    if (apiMessages && apiMessages.length > 1) {
                        const gptResponse = apiMessages.find((msg) => msg.role === 'gpt');
    
                        // Fix: Replace single quotes with double quotes to convert to valid JSON
                        const jsonString = gptResponse.results.replace(/'/g, '"');
                        const resultItems = JSON.parse(jsonString); // Parsing to JavaScript array
    
                        const mockResults = {
                            results: resultItems.map((item, index) => ({
                                class_index: index + 1,
                                class_name: item,
                            })),
                        };
    
                        // Update state with the transformed mock output
                        setPrediction(mockResults);
                        console.log(mockResults);
                    }
                } catch (error) {
                    console.error('Error fetching classification results:', error);
                } finally {
                    // Set loading state to false once API call completes
                    setIsLoading(false);
                }
            };
    
            // Handle error during file reading
            reader.onerror = (error) => {
                console.error('Error reading file as Base64:', error);
                setIsLoading(false); // Set loading state to false if reading fails
            };
        } catch (error) {
            console.error('Error processing image:', error);
            setIsLoading(false); // Set loading state to false if any other error occurs
        }
    };
    
    
    const handleButtonClick = (model) => {
        const ingredients = prediction.results?.map(item => item.class_name).join(',');
        // Navigate to ChatPage with the ingredient as a parameter
        console.log(`/chat?ingredient=${encodeURIComponent(ingredients)}&model=${encodeURIComponent(model)}`)
        router.push(`/chat?ingredient=${encodeURIComponent(ingredients)}&model=${encodeURIComponent(model)}`);
    };

    // UI View
    return (
        <div className="space-y-6">
            {/* Results Table */}
            {prediction && (
                <div className="bg-white rounded-lg shadow-md overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Index
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Class
                                    </th>
                                    {/* <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Probability
                                    </th> */}
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {prediction.results?.map((item, idx) => (
                                    <tr key={idx} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {item.class_index}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {item.class_name}
                                        </td>
                                        {/* <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {(item.probability * 100).toFixed(2)}%
                                        </td> */}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Image Upload Area */}
            <div
                onClick={handleImageUploadClick}
                className={`
                    relative cursor-pointer
                    border-2 border-dashed border-gray-300 rounded-lg
                    bg-gray-50 hover:bg-gray-100 transition-colors
                    min-h-[400px] flex flex-col items-center justify-center
                    ${isLoading ? 'opacity-50 pointer-events-none' : ''}
                `}
            >
                <input
                    type="file"
                    accept="image/*"
                    capture="camera"
                    className="hidden"
                    ref={inputFile}
                    onChange={handleOnChange}
                />

                {image ? (
                    <div className="w-full h-full p-4">
                        <img
                            src={image}
                            alt="Preview"
                            className="w-full h-full object-contain rounded-lg"
                        />
                    </div>
                ) : (
                    <div className="text-center p-6">
                        <div className="flex flex-col items-center gap-4">
                            <div className="p-4 bg-purple-100 rounded-full">
                                <CloudUpload className="text-purple-500 w-8 h-8" />
                            </div>
                            <div className="space-y-2">
                                <p className="text-gray-700 font-semibold">
                                    Click to upload an image
                                </p>
                                <p className="text-sm text-gray-500">
                                    or drag and drop
                                </p>
                            </div>
                            <button className="mt-4 flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-full hover:bg-purple-600 transition-colors">
                                <CameraAlt className="w-5 h-5" />
                                Take Photo
                            </button>
                        </div>
                    </div>
                )}

                {/* Loading Overlay */}
                {isLoading && (
                    <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
                    </div>
                )}
            </div>

            {/* Debug Output
            {prediction && (
                <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm font-mono text-gray-600 overflow-x-auto">
                        {JSON.stringify(prediction, null, 2)}
                    </p>
                </div>
            )} */}

            {/* Continue Button */}
            {/* {prediction && (
                <button
                    onClick={handleContinueClick}
                    className="button-primary"
                >
                    Continue
                </button>
            )} */}

            {prediction && (
                <div className="flex flex-wrap justify-center gap-4">
                    <button 
                        onClick={() => handleButtonClick('llm')}
                        className="button-primary"
                    >
                        AI Assistant (LLM)
                    </button>
                    <button 
                        onClick={() => handleButtonClick('llm-rag')}
                        className="button-secondary">
                    AI Expert (LLM-RAG)
                        </button>
                </div>
            )}

        </div>
    );
}