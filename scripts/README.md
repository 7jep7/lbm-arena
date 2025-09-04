# Production Scripts

This folder contains **production-safe** scripts for LBM Arena.

## Production Scripts

### `init_db_safe.py`
- **Purpose**: Safe database initialization for production
- **Behavior**: Creates tables if they don't exist, never adds test data
- **Usage**: Automatically used during deployment via `build.sh`
- **Safety**: ✅ Production safe - will not overwrite or modify existing data

### `verify_deployment.py`
- **Purpose**: Verify deployment is working correctly
- **Behavior**: Tests API endpoints to ensure they respond correctly
- **Usage**: Can be run after deployment to verify everything works
- **Safety**: ✅ Read-only operations, no data modification

## Development Scripts

For development and testing scripts, see the `dev/` folder.

⚠️ **Never use development scripts in production!** They can delete data and overwrite your database.

## Usage in Production

The production deployment automatically uses `init_db_safe.py` through the build process defined in `build.sh`. This ensures:

- Tables are created if missing
- No test data is added
- Existing data is never touched
- Database starts empty and grows through user interactions

## Manual Usage

If you need to manually initialize the database in production:

```bash
python scripts/init_db_safe.py
```

To verify a deployment:

```bash
python scripts/verify_deployment.py
```
