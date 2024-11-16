'use client';

import Link from 'next/link';

export default function Home() {
    return (
        <div className="page-wrapper">
            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-content">
                    <h1 className="hero-title">
                        I'm your daily meal assistant!
                    </h1>
                    <span className="text-8xl">😉</span>

                    <p className="hero-description">
                        Empty your fridge, cook amazing food, and wow all your family and friends.
                    </p>
                    <div className="flex flex-wrap justify-center gap-4">
                        <button className="button-primary">Get Started</button>
                        <button className="button-secondary">Learn More</button>
                    </div>
                </div>
            </section>

            {/* Content Section */}
            <section id="content-section" className="content-section min-h-screen pt-20 pb-12 px-4 bg-white">
                <div className="container mx-auto max-w-3xl">
                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-500 to-orange-400 font-montserrat">
                            Image Classification
                        </h1>
                        <p className="text-gray-600 mt-2">
                            Upload an image to classify its contents using AI.
                        </p>
                    </div>

                    {/* Image Classification Component */}
                    <div className="border border-gray-300 p-4 rounded-lg shadow-md text-center">
                        <p className="text-gray-500 italic">[Image Classification Component Placeholder]</p>
                    </div>
                </div>
            </section>
            {/* </> */}

            {/* Content Section */}
            {/* <section className="content-section"> */}

                {/* <div className="content-grid"> */}

                    {/* <Link href="/image" className="block">
                        <div className="feature-card">
                            <h3 className="feature-card-title">Capture your Fridge</h3>
                            <p className="feature-card-description">
                                Lorem ipsum dolor sit amet, consectetusr adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                            </p>
                        </div>
                    </Link> */}

                    {/* <Link href="/audio" className="block">
                        <div className="feature-card">
                            <h3 className="feature-card-title">Audio 2 Text</h3>
                            <p className="feature-card-description">
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                            </p>
                        </div>
                    </Link>

                    <Link href="/text" className="block">
                        <div className="feature-card">
                            <h3 className="feature-card-title">Text 2 Audio</h3>
                            <p className="feature-card-description">
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                            </p>
                        </div>
                    </Link> */}
                {/* </div> */}
            {/* </section> */}
        </div>
    );
}