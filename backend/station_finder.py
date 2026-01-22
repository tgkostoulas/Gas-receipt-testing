#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gas station finder using Google Places API.
Finds gas station location from merchant name extracted from receipt.
"""

import os
import sys
import requests
from typing import Optional, Dict
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', '')
GOOGLE_PLACES_API_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'

def find_gas_station(merchant_name: str, city: Optional[str] = None, country: str = "Greece", receipt_price: Optional[float] = None) -> Optional[Dict]:
    """
    Find gas station location using Google Places API.
    
    Args:
        merchant_name: Name of gas station from receipt (e.g., "METRO", "SHELL")
        city: Optional city name to narrow search (e.g., "Athens", "Χαλάνδρι")
        country: Country name (default: "Greece")
    
    Returns:
        Dict with station info or None if not found:
        {
            "place_id": "ChIJ...",
            "name": "METRO Gas Station",
            "address": "Full address",
            "latitude": 37.9838,
            "longitude": 23.7275,
            "brand": "METRO" (extracted from name),
            "rating": 4.2,
            "user_ratings_total": 150
        }
    """
    if not GOOGLE_PLACES_API_KEY:
        print("WARNING: GOOGLE_PLACES_API_KEY not set. Cannot search for gas stations.")
        return None
    
    # Build search query
    query_parts = [merchant_name]
    if city:
        query_parts.append(city)
    query_parts.append("gas station")
    query_parts.append(country)
    
    query = " ".join(query_parts)
    
    try:
        response = requests.get(
            GOOGLE_PLACES_API_URL,
            params={
                'query': query,
                'key': GOOGLE_PLACES_API_KEY,
                'type': 'gas_station',  # Filter to gas stations only
                'language': 'el'  # Greek language for results
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Google Places API error: {response.status_code}")
            return None
        
        data = response.json()
        
        if data.get('status') != 'OK' or not data.get('results'):
            print(f"No gas stations found for: {merchant_name}")
            return None
        
        # Get first result (most relevant)
        result = data['results'][0]
        
        # Extract coordinates
        location = result.get('geometry', {}).get('location', {})
        
        # Extract brand from name (simplified)
        brand = merchant_name.upper()
        for common_brand in ['SHELL', 'BP', 'EKO', 'AVIN', 'REVOIL', 'METRO', 'ΑΒ', 'CYCLON']:
            if common_brand in result.get('name', '').upper():
                brand = common_brand
                break
        
        station_data = {
            'place_id': result.get('place_id'),
            'name': result.get('name'),
            'address': result.get('formatted_address'),
            'latitude': location.get('lat'),
            'longitude': location.get('lng'),
            'brand': brand,
            'rating': result.get('rating'),
            'user_ratings_total': result.get('user_ratings_total', 0)
        }
        
        # Get additional details
        details = get_place_details(result.get('place_id'))
        if details:
            station_data.update(details)
        
        # Note: Google Places API does not provide fuel prices
        # We can store the price from the receipt for comparison
        if receipt_price is not None:
            station_data['price_from_receipt'] = receipt_price
            station_data['price_source'] = 'receipt'
        
        return station_data
    
    except Exception as e:
        print(f"Error searching for gas station: {str(e)}")
        return None

def get_place_details(place_id: str) -> Optional[Dict]:
    """
    Get detailed information about a place using Places API Details.
    Note: Google Places API does not provide fuel prices, but we can get
    additional info like opening hours, phone number, etc.
    """
    if not GOOGLE_PLACES_API_KEY or not place_id:
        return None
    
    details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
    
    try:
        # Try to get all available fields including fuel prices if available
        # Note: Google Places API may not have fuel prices, but we'll check all fields
        response = requests.get(
            details_url,
            params={
                'place_id': place_id,
                'key': GOOGLE_PLACES_API_KEY,
                'fields': 'name,formatted_phone_number,opening_hours,website,price_level,current_opening_hours,editorial_summary,reviews',
                'language': 'el'
            },
            timeout=10
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if data.get('status') != 'OK' or not data.get('result'):
            return None
        
        result = data['result']
        details = {}
        
        if result.get('formatted_phone_number'):
            details['phone'] = result.get('formatted_phone_number')
        if result.get('website'):
            details['website'] = result.get('website')
        if result.get('opening_hours'):
            details['opening_hours'] = result.get('opening_hours', {}).get('weekday_text', [])
        
        # Check ALL fields in the response for any fuel price information
        # Google Places API typically doesn't provide fuel prices, but let's check everything
        fuel_price_data = {}
        
        # Check every field in the result
        for key, value in result.items():
            key_lower = key.lower()
            # Look for any field that might contain fuel/price info
            if any(term in key_lower for term in ['fuel', 'price', 'gas', 'petrol', 'diesel', 'unleaded']):
                fuel_price_data[key] = value
                details[f'google_{key}'] = value
        
        # Check for fuelOptions (if it exists in newer API versions)
        if 'fuelOptions' in result:
            fuel_price_data['fuelOptions'] = result['fuelOptions']
            details['fuel_prices'] = result['fuelOptions']
        
        # Check reviews/editorial summary for price mentions (sometimes prices are mentioned)
        if result.get('editorial_summary'):
            summary = result.get('editorial_summary', {}).get('overview', '')
            if summary:
                details['editorial_summary'] = summary
        
        # Store any fuel price data found
        if fuel_price_data:
            details['google_fuel_price_data'] = fuel_price_data
            print(f"Found potential fuel price fields: {list(fuel_price_data.keys())}")
        else:
            # Google Places API does not provide fuel prices in standard fields
            # This is expected - Google doesn't track fuel prices
            pass
        
        return details
    
    except Exception as e:
        print(f"Error getting place details: {str(e)}")
        return None

def find_gas_station_by_address(address: str) -> Optional[Dict]:
    """
    Find gas station by address using Geocoding API.
    Useful if receipt contains full address.
    """
    if not GOOGLE_PLACES_API_KEY:
        return None
    
    geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    
    try:
        response = requests.get(
            geocode_url,
            params={
                'address': f"{address}, Greece",
                'key': GOOGLE_PLACES_API_KEY
            },
            timeout=10
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if data.get('status') != 'OK' or not data.get('results'):
            return None
        
        result = data['results'][0]
        location = result.get('geometry', {}).get('location', {})
        
        return {
            'address': result.get('formatted_address'),
            'latitude': location.get('lat'),
            'longitude': location.get('lng'),
            'place_id': result.get('place_id')
        }
    
    except Exception as e:
        print(f"Error geocoding address: {str(e)}")
        return None

# Example usage
if __name__ == '__main__':
    # Test with a known gas station
    station = find_gas_station("METRO", city="Athens")
    if station:
        print(f"Found: {station['name']}")
        print(f"Address: {station['address']}")
        print(f"Location: {station['latitude']}, {station['longitude']}")
    else:
        print("Station not found. Make sure GOOGLE_PLACES_API_KEY is set.")
