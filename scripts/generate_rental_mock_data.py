#!/usr/bin/env python3
"""
Generate mock rental data and load directly to Supabase
"""
import os
import sys
from datetime import date, timedelta
from decimal import Decimal
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client

SUPABASE_URL = "https://tnnsfheflydiuhiduntn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRubnNmaGVmbHlkaXVoaWR1bnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1MTIxMjMsImV4cCI6MjA4MjA4ODEyM30.XZs44a7bNOrV2s6Aexne1sTP261L8wCprOSPO7XTuJo"

# Dubai communities with realistic rental prices
COMMUNITIES = [
    ("Dubai Marina", 80000, 150000),
    ("Downtown Dubai", 90000, 200000),
    ("Palm Jumeirah", 150000, 400000),
    ("Business Bay", 70000, 140000),
    ("JBR", 85000, 180000),
    ("JVC", 45000, 85000),
    ("JVT", 50000, 90000),
    ("Dubai Hills Estate", 75000, 160000),
    ("Arabian Ranches", 95000, 180000),
    ("Motor City", 50000, 95000),
    ("Sports City", 40000, 75000),
    ("International City", 28000, 55000),
    ("Dubai South", 35000, 70000),
    ("Town Square", 55000, 100000),
    ("Al Furjan", 60000, 110000),
]

PROPERTY_TYPES = ["Apartment", "Villa", "Townhouse"]
ROOMS_BUCKETS = ["Studio", "1BR", "2BR", "3BR", "4BR+"]

def generate_rental_data():
    """Generate realistic rental data"""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    records = []
    period_date = date(2025, 12, 1)  # December 2025
    
    for community, min_rent, max_rent in COMMUNITIES:
        for rooms in ROOMS_BUCKETS:
            # Calculate realistic rent based on rooms
            if rooms == "Studio":
                base_rent = min_rent
            elif rooms == "1BR":
                base_rent = min_rent * 1.3
            elif rooms == "2BR":
                base_rent = min_rent * 1.7
            elif rooms == "3BR":
                base_rent = min_rent * 2.2
            else:  # 4BR+
                base_rent = max_rent
            
            # Add some variation
            avg_rent = base_rent * random.uniform(0.9, 1.1)
            median_rent = avg_rent * random.uniform(0.95, 1.05)
            rent_count = random.randint(20, 150)
            
            record = {
                "period_date": period_date.isoformat(),
                "community": community,
                "property_type": random.choice(PROPERTY_TYPES),
                "rooms_bucket": rooms,
                "avg_rent_aed": round(avg_rent, 2),
                "median_rent_aed": round(median_rent, 2),
                "rent_count": rent_count
            }
            records.append(record)
    
    print(f"Generated {len(records)} rental records")
    
    # Insert in batches
    batch_size = 50
    inserted = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            result = supabase.table("rental_index").upsert(batch).execute()
            inserted += len(batch)
            print(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
        except Exception as e:
            print(f"Error inserting batch: {e}")
    
    print(f"\n✅ Total inserted: {inserted} rental records")
    
    # Verify
    count_result = supabase.table("rental_index").select("*", count="exact").execute()
    print(f"✅ Total in database: {count_result.count} records")

if __name__ == "__main__":
    generate_rental_data()
