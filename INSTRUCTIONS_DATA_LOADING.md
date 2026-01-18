# Instructions pour charger les données manquantes

## Problème identifié
Les tables `rental_index`, `developers_pipeline`, et `listings` sont vides ou n'existent pas dans le schéma `public` de Supabase.

---

## Solution : Créer les tables via Supabase Dashboard

### Étape 1 : Accéder à Supabase SQL Editor

1. Ouvre https://supabase.com/dashboard
2. Sélectionne le projet `tnnsfheflydiuhiduntn`
3. Va dans **SQL Editor** (menu gauche)

### Étape 2 : Créer la table `rental_index`

Copie et exécute ce SQL :

```sql
-- Create rental_index table in public schema
CREATE TABLE IF NOT EXISTS public.rental_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_date DATE NOT NULL,
    
    -- Location
    community VARCHAR(255),
    project VARCHAR(255),
    
    -- Property
    property_type VARCHAR(100),
    rooms_bucket VARCHAR(20),
    
    -- Rental data
    avg_rent_aed DECIMAL(12, 2),
    median_rent_aed DECIMAL(12, 2),
    rent_count INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE (period_date, community, project, property_type, rooms_bucket)
);

CREATE INDEX IF NOT EXISTS idx_rental_period ON public.rental_index (period_date DESC);
CREATE INDEX IF NOT EXISTS idx_rental_community ON public.rental_index (community);

-- Enable RLS (Row Level Security)
ALTER TABLE public.rental_index ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust as needed)
CREATE POLICY "Allow all operations on rental_index" ON public.rental_index
    FOR ALL USING (true) WITH CHECK (true);
```

### Étape 3 : Créer la table `developers_pipeline`

```sql
-- Create developers_pipeline table in public schema
CREATE TABLE IF NOT EXISTS public.developers_pipeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name VARCHAR(255) NOT NULL,
    developer VARCHAR(255),
    
    -- Location
    community VARCHAR(255),
    
    -- Supply
    total_units INTEGER,
    units_by_type JSONB,
    
    -- Timeline
    launch_date DATE,
    expected_handover_date DATE,
    actual_handover_date DATE,
    
    -- Status
    status VARCHAR(50),
    completion_percentage DECIMAL(5, 2),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_handover_date ON public.developers_pipeline (expected_handover_date);
CREATE INDEX IF NOT EXISTS idx_developer_community ON public.developers_pipeline (community);

-- Enable RLS
ALTER TABLE public.developers_pipeline ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Allow all operations on developers_pipeline" ON public.developers_pipeline
    FOR ALL USING (true) WITH CHECK (true);
```

### Étape 4 : Créer la table `listings`

```sql
-- Create listings table in public schema
CREATE TABLE IF NOT EXISTS public.listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id VARCHAR(255) UNIQUE NOT NULL,
    listing_date DATE NOT NULL,
    
    -- Location
    community VARCHAR(255),
    project VARCHAR(255),
    building VARCHAR(255),
    
    -- Property
    property_type VARCHAR(100),
    rooms_bucket VARCHAR(20),
    area_sqft DECIMAL(10, 2),
    
    -- Price
    asking_price_aed DECIMAL(15, 2),
    asking_price_per_sqft DECIMAL(10, 2),
    
    -- History
    original_price_aed DECIMAL(15, 2),
    price_changes INTEGER DEFAULT 0,
    last_price_change_date DATE,
    days_on_market INTEGER,
    
    -- Status
    status VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_listing_date ON public.listings (listing_date DESC);
CREATE INDEX IF NOT EXISTS idx_listing_community ON public.listings (community);
CREATE INDEX IF NOT EXISTS idx_listing_status ON public.listings (status);

-- Enable RLS
ALTER TABLE public.listings ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Allow all operations on listings" ON public.listings
    FOR ALL USING (true) WITH CHECK (true);
```

---

## Étape 5 : Charger les données mock

Une fois les tables créées, exécute :

```bash
cd /Users/adrienbeyondcrypto/Desktop/Robin
node scripts/load_rental_data_node.js
```

Ou via le data loader Next.js :
```
http://localhost:3000/data-loader
```

---

## Vérification

Après création des tables, vérifie :

```bash
cd /Users/adrienbeyondcrypto/Desktop/Robin/next-app
node -e "
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(
  'https://tnnsfheflydiuhiduntn.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRubnNmaGVmbHlkaXVoaWR1bnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1MTIxMjMsImV4cCI6MjA4MjA4ODEyM30.XZs44a7bNOrV2s6Aexne1sTP261L8wCprOSPO7XTuJo'
);

async function check() {
  const tables = ['rental_index', 'developers_pipeline', 'listings'];
  for (const table of tables) {
    const { count, error } = await supabase.from(table).select('*', { count: 'exact', head: true });
    console.log(\`\${table}: \${error ? 'ERROR - ' + error.message : count + ' records'}\`);
  }
}
check();
"
```

---

## Alternative : Utiliser le Data Loader UI

1. Ouvre `http://localhost:3000/data-loader`
2. Clique sur "Load Sample Data" pour charger des données de test
3. Vérifie les compteurs de chaque table

---

## Prochaines étapes après chargement

1. ✅ Vérifier que `rental_index` a 75+ records
2. ✅ Régénérer les opportunités (100+ deals)
3. ✅ Charger `developers_pipeline` (50+ projets)
4. ✅ Tester l'API `/api/yield` → devrait montrer des yields réels
5. ✅ Vérifier la page `/yield` → indicateurs "✓ Real data"

---

## Contact

Si les tables ne se créent pas, vérifie :
- Les permissions RLS (Row Level Security)
- Le rôle `anon` a bien accès aux tables
- Les policies sont correctement configurées
