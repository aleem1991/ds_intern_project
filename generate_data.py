import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# --- Configuration ---
NUM_TRIPS = 1000
START_DATE = datetime(2025, 5, 1)
END_DATE = datetime(2025, 7, 22)
PLATFORMS = ['Uber', 'Lyft']
FUEL_COST_PER_KM = 0.12  # Average cost for fuel
MAINTENANCE_COST_PER_KM = 0.08 # Average cost for wear & tear
# ---------------------

def create_trip_data(num_trips):
    """Generates a list of synthetic trip data."""
    trip_data = []
    current_date = START_DATE
    
    for i in range(num_trips):
        platform = random.choice(PLATFORMS)
        trip_date = START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))
        
        trip_duration_minutes = random.randint(5, 45)
        wait_time_minutes = random.randint(2, 15)
        trip_distance_km = round(random.uniform(2.0, 30.0), 2)
        
        # Simulate fare based on distance and duration
        base_fare = 2.50
        fare = base_fare + (trip_distance_km * 1.1) + (trip_duration_minutes * 0.25)
        gross_fare = round(fare * random.uniform(0.9, 1.3), 2) # Add some variability/surge
        
        if platform == 'Uber':
            commission_percent = 0.25
        else: # Lyft
            commission_percent = 0.28
            
        trip_data.append({
            'trip_id': 1000 + i,
            'date': trip_date.date(),
            'platform': platform,
            'trip_duration_minutes': trip_duration_minutes,
            'wait_time_minutes': wait_time_minutes,
            'total_time_minutes': trip_duration_minutes + wait_time_minutes,
            'trip_distance_km': trip_distance_km,
            'gross_fare': gross_fare,
            'platform_commission_percent': commission_percent,
        })
        
    return trip_data

print("Generating synthetic gig work data...")
trips = create_trip_data(NUM_TRIPS)
df = pd.DataFrame(trips)

# --- Feature Engineering: Calculate Costs and Profits ---
print("Calculating costs and profits...")
df['platform_fees'] = df['gross_fare'] * df['platform_commission_percent']
df['net_earnings'] = df['gross_fare'] - df['platform_fees']
df['vehicle_costs'] = (df['trip_distance_km'] * FUEL_COST_PER_KM) + (df['trip_distance_km'] * MAINTENANCE_COST_PER_KM)
df['true_profit'] = df['net_earnings'] - df['vehicle_costs']

# Save to a CSV file
output_filename = 'gig_work_data.csv'
df.to_csv(output_filename, index=False)

print(f"Success! Data saved to '{output_filename}'")