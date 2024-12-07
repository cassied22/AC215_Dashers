import { NextResponse } from 'next/server';

export async function GET(req) {
    const { searchParams } = new URL(req.url);
    const keyword = searchParams.get('keyword');
    const apiKey = process.env.GOOGLE_PLACES_API_KEY;
    const location = '42.373611,-71.109733'; // Default location (Harvard SEAS)
    const radius = 1500; // Radius in meters

    try {
        const response = await fetch(
            `https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=${location}&radius=${radius}&type=restaurant&keyword=${keyword}&key=${apiKey}`
        );

        if (!response.ok) {
            throw new Error('Failed to fetch data from Google Places API');
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error('Error in API route:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
