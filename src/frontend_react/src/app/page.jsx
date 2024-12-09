'use client';

import React from 'react';
import ImageClassification from '@/components/image/ImageClassification';

export default function Home() {

    const scrollToContent = () => {
        document.getElementById('content-section').scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <div className="page-wrapper">
            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-content">
                    <h1 className="hero-title">
                        I'm your daily meal assistant Dasher!
                    </h1>
                    <span className="text-8xl">😉</span>

                    <p className="hero-description">
                        Empty your fridge, cook amazing food, and wow all your family and friends.
                    </p>
                    <div className="flex flex-wrap justify-center gap-4">
                        {/* <button className="button-primary">Get Started</button> */}
                        <button
                            className="button-primary"
                            onClick={scrollToContent}
                        >
                            Get Started
                        </button>
                        <button
                            className="button-secondary"
                            onMouseEnter={(e) => e.target.innerText = "Coming Soon"}
                            onMouseLeave={(e) => e.target.innerText = "Medium Post"}
                        >
                            Medium Post
                        </button>
                    </div>
                </div>
            </section>

            {/* Content Section */}
            <section id="content-section" className="content-section min-h-screen pt-20 pb-12 px-4 bg-white">
                <div className="container mx-auto max-w-3xl">
                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-500 to-orange-400 font-montserrat">
                            Let's see what's in your fridge!
                        </h1>
                        <p className="text-gray-600 mt-2">
                            Take a picture or upload an image for recognition using AI.
                        </p>
                    </div>

                    {/* Image Classification Component */}
                    <ImageClassification />

                    
                </div>
            </section>
        </div>
    );
}