#!/usr/bin/env node
/**
 * Generate and load rental mock data to Supabase
 */
const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = 'https://tnnsfheflydiuhiduntn.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRubnNmaGVmbHlkaXVoaWR1bnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1MTIxMjMsImV4cCI6MjA4MjA4ODEyM30.XZs44a7bNOrV2s6Aexne1sTP261L8wCprOSPO7XTuJo';

const COMMUNITIES = [
  ['Dubai Marina', 80000, 150000],
  ['Downtown Dubai', 90000, 200000],
  ['Palm Jumeirah', 150000, 400000],
  ['Business Bay', 70000, 140000],
  ['JBR', 85000, 180000],
  ['JVC', 45000, 85000],
  ['JVT', 50000, 90000],
  ['Dubai Hills Estate', 75000, 160000],
  ['Arabian Ranches', 95000, 180000],
  ['Motor City', 50000, 95000],
  ['Sports City', 40000, 75000],
  ['International City', 28000, 55000],
  ['Dubai South', 35000, 70000],
  ['Town Square', 55000, 100000],
  ['Al Furjan', 60000, 110000],
  ['Mirdif', 65000, 120000],
  ['Al Barsha', 55000, 105000],
  ['Dubai Silicon Oasis', 38000, 72000],
  ['Jumeirah Village', 48000, 88000],
  ['Jumeirah', 120000, 280000],
];

const PROPERTY_TYPES = ['Apartment', 'Villa', 'Townhouse'];
const ROOMS_BUCKETS = ['Studio', '1BR', '2BR', '3BR', '4BR+'];

function random(min, max) {
  return Math.random() * (max - min) + min;
}

function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

async function generateRentalData() {
  const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
  
  const records = [];
  const periodDate = '2025-12-01';
  
  for (const [community, minRent, maxRent] of COMMUNITIES) {
    for (const rooms of ROOMS_BUCKETS) {
      let baseRent;
      if (rooms === 'Studio') baseRent = minRent;
      else if (rooms === '1BR') baseRent = minRent * 1.3;
      else if (rooms === '2BR') baseRent = minRent * 1.7;
      else if (rooms === '3BR') baseRent = minRent * 2.2;
      else baseRent = maxRent;
      
      const avgRent = baseRent * random(0.9, 1.1);
      const medianRent = avgRent * random(0.95, 1.05);
      const rentCount = Math.floor(random(20, 150));
      
      records.push({
        period_date: periodDate,
        community: community,
        property_type: randomChoice(PROPERTY_TYPES),
        rooms_bucket: rooms,
        avg_rent_aed: Math.round(avgRent * 100) / 100,
        median_rent_aed: Math.round(medianRent * 100) / 100,
        rent_count: rentCount
      });
    }
  }
  
  console.log(`Generated ${records.length} rental records`);
  
  // Insert in batches
  const batchSize = 50;
  let inserted = 0;
  
  for (let i = 0; i < records.length; i += batchSize) {
    const batch = records.slice(i, i + batchSize);
    try {
      const { data, error } = await supabase
        .from('rental_index')
        .upsert(batch);
      
      if (error) throw error;
      
      inserted += batch.length;
      console.log(`Inserted batch ${Math.floor(i / batchSize) + 1}: ${batch.length} records`);
    } catch (error) {
      console.error(`Error inserting batch:`, error.message);
    }
  }
  
  console.log(`\n✅ Total inserted: ${inserted} rental records`);
  
  // Verify
  const { count, error } = await supabase
    .from('rental_index')
    .select('*', { count: 'exact', head: true });
  
  if (!error) {
    console.log(`✅ Total in database: ${count} records`);
  }
}

generateRentalData().catch(console.error);
