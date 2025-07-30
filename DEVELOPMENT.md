# Development Setup

## API Keys Configuration

This project uses different API keys for development and production environments.

### Development Setup

1. Copy the development config template:
   ```bash
   cp _config_dev.yml.template _config_dev.yml
   ```

2. Edit `_config_dev.yml` and add your development API keys:
   ```yaml
   google_api:
     maps_key: "YOUR_DEV_MAPS_API_KEY"
     weather_key: "YOUR_DEV_WEATHER_API_KEY"
   ```

3. Run Jekyll with the development config:

   **Command Line:**
   ```bash
   # Development (uses _config_dev.yml keys)
   bundle exec jekyll serve --config _config.yml,_config_dev.yml
   
   # Production (uses _config.yml keys)
   bundle exec jekyll serve
   ```

   **VS Code:**
   - Use the "Jekyll Serve (Development)" task: `Ctrl/Cmd + Shift + P` → "Tasks: Run Task" → "Jekyll Serve (Development)"
   - Or use the Jekyll plugin (configured via `.vscode/settings.json` to use dev config automatically)

### How It Works

- **Development**: When you run Jekyll with `--config _config.yml,_config_dev.yml`, the development keys from `_config_dev.yml` override the production keys
- **Production**: When deployed (without the dev config), it uses the production keys from `_config.yml`
- **Security**: `_config_dev.yml` is gitignored, so your development keys won't be committed

### Files

- `_config.yml` - Contains production API keys (safe to commit)
- `_config_dev.yml` - Contains development API keys (gitignored, DO NOT commit)
- `_config_dev.yml.template` - Template for setting up development keys