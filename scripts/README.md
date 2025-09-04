# Scripts - Testing & Debugging Utilities

This folder contains utility scripts for testing, debugging, and database management.

## Database Scripts

### `create_db.py`
Creates all database tables in Supabase.
```bash
python scripts/create_db.py
```

### `add_test_data.py` 
Adds initial test data (players and games) if database is empty.
```bash
python scripts/add_test_data.py
```

### `add_two_players.py`
Adds 2 additional players to existing database.
```bash
python scripts/add_two_players.py
```

### `reset_test_data.py`
Clears all data and adds fresh test data (6 players, 5 games).
```bash
python scripts/reset_test_data.py
```

## Testing Scripts

### `test_setup.py`
Tests basic imports and environment setup.
```bash
python scripts/test_setup.py
```

## Usage

All scripts should be run from the project root directory with the conda environment activated:

```bash
# Activate environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /mnt/nvme0n1p8/conda-envs/lbm-arena

# Run any script
python scripts/script_name.py
```

## Current Database State

After running `add_two_players.py`, the database contains:

**Players (6 total):**
- GPT-4 (OpenAI)
- Claude-3 (Anthropic) 
- GPT-3.5 (OpenAI)
- Test-Bot (Custom)
- Gemini-Pro (Google) 
- LLaMA-2 (Meta)

**Games (3+ total):**
- Various chess and poker games between the players
- Mix of completed and in-progress games
