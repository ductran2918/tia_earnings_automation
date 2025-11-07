# Supabase Database Notes

## Issue: Missing Auto-Increment on Primary Key

### Common Names for This Issue
- "Missing SERIAL/BIGSERIAL on Primary Key" (PostgreSQL-specific)
- "Primary Key Auto-Increment Not Configured"
- "NOT NULL Constraint Violation on Primary Key"
- "Missing Default Value on ID Column"

### Error Message
```
null value in column "id" of relation "<table_name>" violates not-null constraint
```

**Example from Sea Group Implementation:**
```
❌ Push failed: Supabase error: {
  'message': 'null value in column "id" of relation "seagroup_metrics" violates not-null constraint',
  'code': '23502',
  'hint': None,
  'details': 'Failing row contains (null, sea-group-garena, 2025-04-01, ...)'
}
```

### Root Cause
The `id` column in the Supabase table was created as PRIMARY KEY with NOT NULL constraint, but it's missing auto-generation configuration. PostgreSQL requires either:
- `BIGSERIAL` or `SERIAL` data type (which automatically creates a sequence)
- `DEFAULT nextval('sequence_name')` to generate IDs automatically

When you try to INSERT a row without providing an `id` value (or with `id: null`), PostgreSQL enforces the NOT NULL constraint and rejects the operation.

### Fix for Existing Tables

If you've already created a table without auto-increment, apply this SQL fix in Supabase SQL Editor:

```sql
-- Step 1: Change column type to BIGINT (if not already)
ALTER TABLE public.seagroup_metrics
ALTER COLUMN id SET DATA TYPE BIGINT;

-- Step 2: Create a sequence for the ID column
CREATE SEQUENCE IF NOT EXISTS seagroup_metrics_id_seq;

-- Step 3: Set the sequence as default value for the id column
ALTER TABLE public.seagroup_metrics
ALTER COLUMN id SET DEFAULT nextval('seagroup_metrics_id_seq');

-- Step 4: Associate the sequence with the column (for DROP TABLE cascade)
ALTER SEQUENCE seagroup_metrics_id_seq
OWNED BY public.seagroup_metrics.id;

-- Step 5: Set the sequence to start after the current max ID
SELECT setval('seagroup_metrics_id_seq',
  COALESCE((SELECT MAX(id) FROM public.seagroup_metrics), 0) + 1
);
```

### Prevention: Correct Table Creation

When creating new tables in Supabase, always use `BIGSERIAL PRIMARY KEY` for auto-incrementing ID columns:

```sql
CREATE TABLE public.table_name (
    id BIGSERIAL PRIMARY KEY,  -- This automatically creates sequence and default value
    company_slug VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    -- other columns...
);
```

**Alternative (explicit sequence):**
```sql
CREATE SEQUENCE table_name_id_seq;

CREATE TABLE public.table_name (
    id BIGINT PRIMARY KEY DEFAULT nextval('table_name_id_seq'),
    company_slug VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    -- other columns...
);

ALTER SEQUENCE table_name_id_seq OWNED BY public.table_name.id;
```

### Code-Side Prevention

In Python code, always exclude the `id` field when inserting data to Supabase:

```python
# ✅ CORRECT: Exclude 'id' field explicitly
insert_data = {k: v for k, v in extracted_data.items() if k != "id"}

# ❌ WRONG: Including 'id' with null value
insert_data = extracted_data  # Contains "id": null
```

### Context: When This Was Encountered

**Date**: During Sea Group database push implementation (November 2025)

**Scenario**:
- Implemented `push_sea_group_to_supabase()` function in `app/database.py`
- Created Supabase table `public.seagroup_metrics` manually with PRIMARY KEY constraint
- Forgot to configure auto-increment (BIGSERIAL or DEFAULT nextval())
- Encountered error when trying to INSERT first Sea Group record

**Resolution**:
1. Verified code was correctly excluding `id` field using dictionary comprehension
2. Identified table schema issue in Supabase
3. Applied SQL fix to add sequence and default value to existing table
4. Tested INSERT operation - successful with auto-generated ID

### Future Reference Checklist

When implementing database push for new companies (Alibaba, Bukalapak, VNG, etc.):

- [ ] **Before creating table**: Use `BIGSERIAL PRIMARY KEY` for `id` column
- [ ] **Verify table schema**: Check that `id` column has default value configured
- [ ] **Test in SQL Editor**: Run manual INSERT without `id` field to verify auto-generation
- [ ] **Code implementation**: Use dictionary comprehension to exclude `id`: `{k: v for k, v in data.items() if k != "id"}`
- [ ] **Test INSERT**: Push test data through Python code to confirm end-to-end functionality
- [ ] **Test UPDATE**: Verify duplicate detection and UPDATE logic work correctly

### Related Files

- `app/database.py`: Contains `push_*_to_supabase()` functions with `id` field exclusion logic
- `app/sea_group_extraction.py`: Sea Group extraction module (first implementation after Grab)
- `app/grab_extraction.py`: Grab extraction module (reference implementation)
- Supabase tables: `public.grab_metrics`, `public.seagroup_metrics`

### Additional Resources

- [PostgreSQL SERIAL Types Documentation](https://www.postgresql.org/docs/current/datatype-numeric.html#DATATYPE-SERIAL)
- [Supabase SQL Editor](https://supabase.com/dashboard/project/_/sql)
- [Python Supabase Client - Insert Operations](https://supabase.com/docs/reference/python/insert)
