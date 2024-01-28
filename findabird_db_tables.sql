CREATE TABLE IF NOT EXISTS "hotspots" (
  "id" serial PRIMARY KEY,
  "ebird_id" varchar(50),
  "country_id" integer,
  "subnational1_id" integer,
  "subnational2_id" integer,
  "latitude" decimal(9,6),
  "longitude" decimal(9,6),
  "geometry" geometry(point, 4326),
  "display_name" varchar(255),
  "location_private" bool,
  "create_date" timestamp
);

CREATE TABLE IF NOT EXISTS "countries" (
  "id" serial PRIMARY KEY,
  "country_code" varchar(2),
  "display_name" varchar(100)
);

CREATE TABLE IF NOT EXISTS "subnational1" (
  "id" serial PRIMARY KEY,
  "subnational1_code" varchar(10),
  "display_name" varchar(100),
  "country_id" integer
);

CREATE TABLE IF NOT EXISTS "subnational2" (
  "id" serial PRIMARY KEY,
  "subnational2_code" varchar(10),
  "display_name" varchar(100),
  "country_id" integer,
  "subnational1_id" integer
);

CREATE TABLE IF NOT EXISTS "users" (
  "id" serial PRIMARY KEY,
  "ebird_observer_id" varchar(50),
  "first_name" varchar(50),
  "last_name" varchar(50),
  "email" varchar(255)
);

CREATE TABLE IF NOT EXISTS "species" (
  "id" serial PRIMARY KEY,
  "taxonomic_order" integer,
  "common_name" varchar(255),
  "sci_name" varchar(255),
  "order" varchar(100),
  "family" varchar(100),
  "category" varchar(10),
  "avibase_id" varchar(20),
  "species_code" varchar(10),
  "alpha_code_four" varchar(4),
  "alpha_code_six" varchar(6)
);

CREATE TABLE IF NOT EXISTS "observations" (
  "id" serial PRIMARY KEY,
  "ebird_obs_id" varchar(50),
  "checklist_id" integer,
  "species_id" integer,
  "count" integer,
  "observation_reviewed" bool
);

CREATE TABLE IF NOT EXISTS "checklists" (
  "id" serial PRIMARY KEY,
  "ebird_id" varchar(50),
  "user_id" integer,
  "hotspot_id" integer,
  "create_date" timestamp
);

CREATE TABLE IF NOT EXISTS "user_locations" (
  "id" serial PRIMARY KEY,
  "user_id" integer,
  "polygon" GEOMETRY(POLYGON, 4326),
  "location_name" varchar(255)
);

CREATE TABLE IF NOT EXISTS "species_needs" (
  "id" serial PRIMARY KEY,
  "user_id" integer,
  "species_id" integer
);

CREATE TABLE IF NOT EXISTS "match_log" (
  "id" serial PRIMARY KEY,
  "user_id" integer,
  "species_id" integer,
  "observation_id" integer,
  "user_location" integer,
  "match_date" timestamp
);

COMMENT ON COLUMN "subnational1"."subnational1_code" IS 'State in the US';

COMMENT ON COLUMN "subnational2"."subnational2_code" IS 'County/Parish in the US';

ALTER TABLE "hotspots" ADD FOREIGN KEY ("country_id") REFERENCES "countries" ("id");

ALTER TABLE "hotspots" ADD FOREIGN KEY ("subnational1_id") REFERENCES "subnational1" ("id");

ALTER TABLE "hotspots" ADD FOREIGN KEY ("subnational2_id") REFERENCES "subnational2" ("id");

ALTER TABLE "subnational1" ADD FOREIGN KEY ("country_id") REFERENCES "countries" ("id");

ALTER TABLE "subnational2" ADD FOREIGN KEY ("country_id") REFERENCES "countries" ("id");

ALTER TABLE "subnational2" ADD FOREIGN KEY ("subnational1_id") REFERENCES "subnational1" ("id");

ALTER TABLE "observations" ADD FOREIGN KEY ("checklist_id") REFERENCES "checklists" ("id");

ALTER TABLE "observations" ADD FOREIGN KEY ("species_id") REFERENCES "species" ("id");

ALTER TABLE "checklists" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "checklists" ADD FOREIGN KEY ("hotspot_id") REFERENCES "hotspots" ("id");

ALTER TABLE "user_locations" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "species_needs" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "species_needs" ADD FOREIGN KEY ("species_id") REFERENCES "species" ("id");

ALTER TABLE "match_log" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "match_log" ADD FOREIGN KEY ("species_id") REFERENCES "species" ("id");

ALTER TABLE "match_log" ADD FOREIGN KEY ("observation_id") REFERENCES "observations" ("id");

ALTER TABLE "match_log" ADD FOREIGN KEY ("user_location") REFERENCES "user_locations" ("id");
