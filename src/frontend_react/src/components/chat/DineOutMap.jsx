'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api';

const DineOutMap = () => {
    const [location, setLocation] = useState({
        lat: 42.363090224283546, // Harvard SEAS coordinates
        lng: -71.12663009798676,
    });
    const [places, setPlaces] = useState([]);
    const [error, setError] = useState(null);
    const [response, setResponse] = useState('');
    const [searchMessage, setSearchMessage] = useState(''); // State for input message
    const [selectedPlace, setSelectedPlace] = useState(null); // State to store selected place for InfoWindow

    const { isLoaded } = useJsApiLoader({
        googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY,
        libraries: ['places'], // Make sure have the Places library loaded
    });

    // Function to handle the search button click
    const handleSearch = () => {
        fetchNearbyPlaces(searchMessage);
    };

    // Fetch nearby places based on user input or default message
    const fetchNearbyPlaces = useCallback((message = '') => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
                    setLocation({
                        lat: latitude,
                        lng: longitude,
                    });

                    // Initialize the PlacesService and request nearby places
                    const map = new window.google.maps.Map(document.createElement('div'), { center: { lat: latitude, lng: longitude }, zoom: 13 });
                    const service = new window.google.maps.places.PlacesService(map);

                    // Default place type is 'restaurant'
                    let placeType = 'restaurant';

                    if (message.toLowerCase().includes('pizza')) {
                        placeType = 'restaurant'; // Pizza-related search
                    } else if (message.toLowerCase().includes('coffee')) {
                        placeType = 'cafe'; // Coffee-related search
                    }

                    const request = {
                        location: { lat: latitude, lng: longitude },
                        radius: 5000, // Search within 5 kilometers
                        type: [placeType], // Correct place type
                        keyword: message, // Add the keyword to refine the search based on the dish name
                    };

                    service.nearbySearch(request, (results, status) => {
                        if (status === window.google.maps.places.PlacesServiceStatus.OK) {
                            setPlaces(results); // Store the places data
                            setResponse(`Found ${results.length} place(s) for "${message}"`); // Display number of places found
                        } else {
                            setError(`Error fetching places: ${status}`);
                            console.error('Error status:', status);
                        }
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

    // Trigger fetching places when the component loads
    useEffect(() => {
        fetchNearbyPlaces(); // Call function to get user's location and places
    }, [fetchNearbyPlaces]);

    const handleMarkerClick = (place) => {
        setSelectedPlace(place); // Set the selected place for InfoWindow display
    };

    if (!isLoaded) {
        return <div>Loading...</div>;
    }

    return (
        <div className="w-full h-[500px] rounded-lg overflow-hidden">
            {error && <div className="p-4 bg-red-100 text-red-700">{error}</div>}
            {response && <div className="p-4 bg-green-100 text-green-700">{response}</div>}

            {/* Input field for user message */}
            <div className="mb-4">
                <input
                    type="text"
                    value={searchMessage}
                    onChange={(e) => setSearchMessage(e.target.value)} // Update the state on input change
                    className="w-full p-2 border border-gray-300 rounded-md"
                    placeholder="Enter a dish name (e.g. 'pizza', 'burger', 'sushi')"
                />
                <button
                    onClick={handleSearch} // Trigger search on button click
                    className="mt-2 px-4 py-2 bg-blue-500 text-white rounded-md"
                >
                    Search
                </button>
            </div>

            {/* Map component */}
            <GoogleMap
                mapContainerClassName="w-full h-full"
                center={location}
                zoom={13}
            >
                <Marker position={location} />
                {places.map((place, index) => (
                    <Marker
                        key={index}
                        position={{ lat: place.geometry.location.lat(), lng: place.geometry.location.lng() }}
                        title={place.name}
                        onClick={() => handleMarkerClick(place)} // Click marker to show info
                    />
                ))}

                {selectedPlace && (
                    <InfoWindow
                        position={{
                            lat: selectedPlace.geometry.location.lat(),
                            lng: selectedPlace.geometry.location.lng(),
                        }}
                        onCloseClick={() => setSelectedPlace(null)} // Close the info window
                    >
                        <div>
                            <h3>{selectedPlace.name}</h3>
                            <p>{selectedPlace.vicinity}</p>
                            <a
                                href={`https://www.google.com/maps/dir/?api=1&destination=${selectedPlace.geometry.location.lat()},${selectedPlace.geometry.location.lng()}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-500"
                            >
                                Get Directions
                            </a>
                        </div>
                    </InfoWindow>
                )}
            </GoogleMap>
        </div>
    );
};

export default DineOutMap;