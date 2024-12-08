'use client'

import fetchVideos from '@/components/youtube/Video';

export default function MapPage() {
    return (
        <div className="min-h-screen pt-20 pb-12 px-4">
            <div className="container mx-auto max-w-3xl">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-500 to-orange-400 font-montserrat">
                        Watch a video on how to cook it 🥣
                    </h1>
                    <p className="text-gray-600 mt-2">
                        Relax and enjoy! You got it
                    </p>
                </div>

                {/* Image Classification Component */}
                <fetchVideos />
            </div>
        </div>
    );
}