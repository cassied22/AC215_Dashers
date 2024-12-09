'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import DataService from '@/services/DataService';

export default function FetchVideos() {
    const [videoData, setVideoData] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const searchParams = useSearchParams();

    const recipe_name = searchParams.get('recipe_name');

    const fetchVideos = async () => {
        if (!recipe_name) return;
    
        setIsLoading(true);
        try {
            const encodedRecipeName = encodeURIComponent(recipe_name);
            const response = await DataService.SearchYouTube(encodedRecipeName);
    
            const videoResults = response?.videos || []; // Access videos array directly
            console.log('Parsed video data:', videoResults);
    
            setVideoData(videoResults);
        } catch (error) {
            console.error('Error fetching video data:', error.response?.data || error.message);
        } finally {
            setIsLoading(false);
        }
    };
    

    useEffect(() => {
        fetchVideos();
    }, [recipe_name]);

    return (
        <div className="text-gray-500">
            <div className="text-center mb-6">
                Let's find videos/posts for: {recipe_name}
                </div>

            {isLoading && (
                <div className="text-center mb-6">
                    <p className="text-gray-500">Loading videos...</p>
                </div>
            )}

            {!isLoading && videoData.length > 0 && (
                <div className="bg-white rounded-lg shadow-md overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Media
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {videoData.map((video) => (
                                    <tr key={video.url} className="hover:bg-gray-50">
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

            {!isLoading && videoData.length === 0 && (
                <div className="text-center py-6">
                    <p className="text-gray-500">No videos found for the recipe "{recipe_name}".</p>
                </div>
            )}
        </div>
    );
}