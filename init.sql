-- Create the job status type if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'jobstatus') THEN
        CREATE TYPE jobstatus AS ENUM ('PENDING', 'IN_PROGRESS', 'SUCCESS', 'FAILED');
    END IF;
END$$;

-- Create the jobs table if it doesn't exist
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    status jobstatus NOT NULL DEFAULT 'PENDING',
    operation VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create a trigger to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create the trigger if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_trigger 
        WHERE tgname = 'update_jobs_updated_at'
    ) THEN
        CREATE TRIGGER update_jobs_updated_at
        BEFORE UPDATE ON jobs
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    END IF;
END$$;
