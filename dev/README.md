# Development Tools

This folder contains all development-only tools and scripts for LBM Arena.

⚠️ **IMPORTANT**: None of these files should be used in production!

## Structure

```
dev/
├── scripts/          # Database development scripts
│   ├── setup_complete_db.py    # ⚠️  Drops all data! Full reset with test data
│   ├── recreate_db.py          # ⚠️  Drops all tables! Fresh schema
│   ├── add_game_data.py        # Add sample game data
│   ├── add_test_data.py        # Add test players/games
│   ├── add_two_players.py      # Add minimal test players
│   ├── reset_test_data.py      # Reset to clean test state
│   ├── test_setup.py           # Test database setup
│   └── create_db.py            # Basic database creation
├── dev.sh           # Quick development startup (conda)
├── run.sh           # Full development environment setup
└── cleanup.sh       # Environment cleanup utilities
```

## Quick Start

**For development with conda environment:**
```bash
./dev/dev.sh
```

**For development with virtual environment:**
```bash
./dev/run.sh
```

## Database Development Scripts

### ⚠️ Destructive Scripts (use with caution!)

- `setup_complete_db.py` - Complete reset with test data
- `recreate_db.py` - Drop and recreate all tables

### Safe Development Scripts

- `add_*.py` - Add specific test data
- `test_setup.py` - Test your database setup
- `reset_test_data.py` - Reset to clean test state

## Production vs Development

**Production uses:**
- `scripts/init_db_safe.py` - Safe table creation only
- `scripts/verify_deployment.py` - Deployment verification

**Development uses:**
- Everything in `dev/` folder - Full testing capabilities
