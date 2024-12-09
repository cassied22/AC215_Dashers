'use client'

import DineOutMap from '@/components/googleMap/DineOutMap';

export default function MapPage() {
    return (
        <div className="min-h-screen pt-20 pb-12 px-4">
            <div className="container mx-auto max-w-3xl">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-500 to-orange-400 font-montserrat">
                        Let's Dine out 🍴
                    </h1>
                    <p className="text-gray-600 mt-2">
                        What do you want to have?
                    </p>
                </div>

                {/* Image Classification Component */}
                <DineOutMap />
            </div>
        </div>
    );
}