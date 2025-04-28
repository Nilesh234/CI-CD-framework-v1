# Dynamic CI/CD Framework

Auto-generates GitHub Actions workflows from YAML/JSON blueprints or shared Templates

## Structure

- `.github/workflows/generate-pipeline.yml`: Main workflow to regenerate pipelines.
- `blueprint/`: YAML/JSON blueprint files.
- `templates/`: Per-technology template YML files.
- `scripts/generate_pipeline.py`: Script to read blueprint and generate pipeline.
- `requirements.txt`: Python dependencies.
- `.gitignore`: Ignore rules.
- `generated_pipeline/` : output file

## Usage

1. Place your blueprint in `blueprint/`.
2. Push to GitHub.
3. The CI workflow will generate `generated_pipeline/generated-pipeline_yyyy-mm-dd_hh-mm-ss`.