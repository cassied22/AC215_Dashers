'use client';

import React, { useState, useEffect } from 'react';
import { GoogleMap, useJsApiLoader, Marker } from '@react-google-maps/api';

const DineOutMap = () => {
    const [location, setLocation] = useState({
        lat: 42.363090224283546, // Harvard SEAS coordinates
        lng: - 71.12663009798676,
    });
    const [error, setError] = useState(null);

    const { isLoaded } = useJsApiLoader({
        googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY,
    });

    useEffect(() => {
        // Try to get user's current location
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    setLocation({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    });
                },
                (err) => {
                    setError('Could not retrieve location');
                    console.error(err);
                }
            );
        } else {
            setError('Geolocation is not supported by this browser');
        }
    }, []);

    if (!isLoaded) {
        return <div>Loading...</div>;
    }

    return (
        <div className="w-full h-[300px] rounded-lg overflow-hidden">
            {error && (
                <div className="p-4 bg-red-100 text-red-700">{error}</div>
            )}
            <GoogleMap
                mapContainerClassName="w-full h-full"
                center={location}
                zoom={13}
            >
                <Marker position={location} />
            </GoogleMap>
        </div>
    );
};

export default DineOutMap;