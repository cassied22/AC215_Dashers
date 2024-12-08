'use client';

import React, { useState, useEffect } from 'react';
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api';

const DineOutMap = () => {
    const [location, setLocation] = useState({
        lat: 42.363090224283546, // Harvard SEAS coordinates
        lng: -71.12663009798676,
    });
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState(null);
    const [restaurants, setRestaurants] = useState([]);
    const [selectedRestaurant, setSelectedRestaurant] = useState(null);

    const { isLoaded } = useJsApiLoader({
        googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY,
        libraries: ['places'], // Load the Places library
    });

    useEffect(() => {
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

    const handleSearch = () => {
        if (!searchTerm.trim()) return;

        const service = new window.google.maps.places.PlacesService(
            document.createElement('div')
        );

        service.textSearch(
            {
                query: `${searchTerm} restaurants`,
                location: new window.google.maps.LatLng(location.lat, location.lng),
                radius: 1000, // Search within 5 km
            },
            (results, status) => {
                if (status === window.google.maps.places.PlacesServiceStatus.OK) {
                    setRestaurants(results.slice(0, 5)); // Take top 5 results
                } else {
                    setError('No matching restaurants found');
                }
            }
        );
    };

    if (!isLoaded) {
        return <div>Loading...</div>;
    }

    return (
        <div className="w-full h-[500px] rounded-lg overflow-hidden">
            {error && (
                <div className="p-4 bg-red-100 text-red-700">{error}</div>
            )}

            {/* Search Input */}
            <div className="flex items-center gap-2 p-4">
                <input
                    type="text"
                    className="w-full bg-gray-100 border-0 rounded-lg px-4 py-3 pr-12 text-gray-800 
                             placeholder-gray-500 focus:ring-2 focus:ring-purple-500 min-h-[24px] 
                             max-h-[400px] resize-none overflow-hidden leading-relaxed"
                    placeholder="Search for restaurants..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
                <button
                    className="p-2 bg-purple-500 text-white rounded"
                    onClick={handleSearch}
                >
                    Search
                </button>
            </div>

            {/* Map */}
            <GoogleMap
                mapContainerClassName="w-full h-full"
                center={location}
                zoom={13}
            >
                <Marker position={location} label="You" />

                {/* Markers for Restaurants */}
                {restaurants.map((restaurant, index) => (
                    <Marker
                        key={index}
                        position={{
                            lat: restaurant.geometry.location.lat(),
                            lng: restaurant.geometry.location.lng(),
                        }}
                        onClick={() => setSelectedRestaurant(restaurant)}
                    />
                ))}

                {/* Info Window for Selected Restaurant */}
                {selectedRestaurant && (
                    <InfoWindow
                        position={{
                            lat: selectedRestaurant.geometry.location.lat(),
                            lng: selectedRestaurant.geometry.location.lng(),
                        }}
                        onCloseClick={() => setSelectedRestaurant(null)}
                    >
                        <div>
                            <h2 className="font-bold">{selectedRestaurant.name}</h2>
                            <p>{selectedRestaurant.formatted_address}</p>
                            {selectedRestaurant.rating && (
                                <p>Rating: {selectedRestaurant.rating} ⭐</p>
                            )}
                        </div>
                    </InfoWindow>
                )}
            </GoogleMap>
        </div>
    );
};

export default DineOutMap;

