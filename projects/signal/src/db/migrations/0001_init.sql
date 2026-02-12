CREATE TABLE IF NOT EXISTS signal_clients (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug varchar(50) NOT NULL UNIQUE,
  name varchar(255) NOT NULL,
  domain varchar(255) NOT NULL,
  repo varchar(255) NOT NULL,
  config jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS signal_content (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id uuid NOT NULL,
  type varchar(50) NOT NULL,
  title varchar(255) NOT NULL,
  slug varchar(255) NOT NULL,
  status varchar(20) NOT NULL,
  file_path text NOT NULL,
  quality_score integer,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS signal_keywords (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id uuid NOT NULL,
  keyword varchar(255) NOT NULL,
  keyword_group varchar(50) NOT NULL,
  priority integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS signal_rankings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id uuid NOT NULL,
  keyword_id uuid NOT NULL,
  position integer NOT NULL,
  search_engine varchar(50) NOT NULL DEFAULT 'google',
  snapshot_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS signal_jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id uuid NOT NULL,
  job_type varchar(50) NOT NULL,
  status varchar(20) NOT NULL,
  payload jsonb NOT NULL,
  error text,
  created_at timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz
);
