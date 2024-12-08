'use client'

import { useState } from 'react';
import DataService from '@/services/DataService';

export default function VideoList() {
    // Component States
    const [videoData, setVideoData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    // Fetch Video Data from API
    const fetchVideos = async () => {
        setIsLoading(true);
        try {
            // Placeholder payload
            const payload = {
                recipe_name: "Chicken and Broccoli Stir Fry"
            };

            // API call
            const response = await DataService.fetchVideos(payload);
            const apiMessages = response.data.messages;

            if (apiMessages && apiMessages.length > 1) {
                const gptResponse = apiMessages.find((msg) => msg.role === 'gpt');
                
                // Parsing response to extract video names and URLs
                const videoRegex = /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g;
                const videoResults = [];
                let match;

                while ((match = videoRegex.exec(gptResponse.results)) !== null) {
                    videoResults.push({
                        index: videoResults.length + 1,
                        name: match[1],
                        url: match[2],
                    });
                }

                setVideoData(videoResults);
            }
        } catch (error) {
            console.error('Error fetching video data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Trigger the API call when the component mounts
    useState(() => {
        fetchVideos();
    }, []);

    // UI View
    return (
        <div className="space-y-6">
            {/* Results Table */}
            {videoData && (
                <div className="bg-white rounded-lg shadow-md overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Index
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Video Name
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {videoData.map((video) => (
                                    <tr key={video.index} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {video.index}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            <a
                                                href={video.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-blue-500 hover:underline"
                                            >
                                                {video.name}
                                            </a>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Loading Indicator */}
            {isLoading && (
                <div className="text-center py-6">
                    <p className="text-gray-500">Loading videos...</p>
                </div>
            )}
        </div>
    );
}
