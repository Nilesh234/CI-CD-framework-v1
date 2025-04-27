import os
import yaml
import json
from datetime import datetime

# Paths
BLUEPRINT_DIR = 'blueprint'
TEMPLATES_DIR = 'templates'
OUTPUT_FOLDER = 'generated_pipelines'

# Load blueprint (yaml or json)
def load_blueprint():
    yaml_path = os.path.join(BLUEPRINT_DIR, 'pipeline-blueprint.yaml')
    json_path = os.path.join(BLUEPRINT_DIR, 'pipeline-blueprint.json')
    
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)
    elif os.path.exists(json_path):
        with open(json_path, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError('No blueprint file found!')

# Load template for a given technology
def load_template(technology):
    template_file = f'{technology.lower()}-template.yml'
    template_path = os.path.join(TEMPLATES_DIR, template_file)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f'Template for {technology} not found at {template_path}')
    
    with open(template_path, 'r') as f:
        return f.read()

# Replace placeholders in the template with values from the blueprint
def fill_template(template_content, blueprint):
    replacements = {
        'PROJECT_NAME': blueprint.get('project_name', 'MyProject'),
        'BRANCHES_PLACEHOLDER': str(blueprint.get('branching', {}).get('allowed_branches', ['main'])),
        'DEPLOY_METHOD': blueprint.get('deployment_target', {}).get('deployment_method', 'sam'),
        'BUILD_TYPE': blueprint.get('build_type', 'full'),
        'LINT_STAGE': str(blueprint.get('stages', {}).get('lint', False)),
        'STATIC_ANALYSIS_STAGE': str(blueprint.get('stages', {}).get('static_analysis', False)),
        'UNIT_TESTS_STAGE': str(blueprint.get('stages', {}).get('unit_tests', False)),
        'INTEGRATION_TESTS_STAGE': str(blueprint.get('stages', {}).get('integration_tests', False)),
        'SECURITY_SCAN_STAGE': str(blueprint.get('stages', {}).get('security_scan', False)),
        'PACKAGE_ARTIFACT_STAGE': str(blueprint.get('stages', {}).get('package_artifact', False)),
        'DEPLOY_STAGE': str(blueprint.get('stages', {}).get('deploy', False)),
        'CLOUD_PROVIDER': blueprint.get('deployment_target', {}).get('cloud_provider', 'aws'),
        'REGION': blueprint.get('deployment_target', {}).get('region', 'us-east-1'),
        'SERVICE': blueprint.get('deployment_target', {}).get('service', 'lambda'),
        'ENVIRONMENT': blueprint.get('deployment_target', {}).get('environment', 'dev')
    }
    
    for placeholder, value in replacements.items():
        if isinstance(value, list):
            # YAML expects a list like ["main", "dev"]
            value = str(value).replace("'", '"')
        template_content = template_content.replace(placeholder, str(value))
    
    return template_content

# Save the final pipeline with a timestamp in a separate folder
def save_pipeline(content):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"generated-pipeline_{timestamp}.yml"  # Filename with timestamp
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"Pipeline generated successfully at {output_path}")

# Main flow
def main():
    # Check if blueprint exists
    blueprint_exists = os.path.exists(os.path.join(BLUEPRINT_DIR, 'pipeline-blueprint.json')) or os.path.exists(os.path.join(BLUEPRINT_DIR, 'pipeline-blueprint.yaml'))
    
    if blueprint_exists:
        print("Generating pipeline from blueprint...")
        blueprint = load_blueprint()
        technology = blueprint.get('technology', 'python')  # default to python
        template_content = load_template(technology)
        filled_content = fill_template(template_content, blueprint)
        save_pipeline(filled_content)
    
    else:
        # If no blueprint, fall back to generating from template
        print("Generating pipeline from template...")
        template_name = 'python'  # Default template if no blueprint, you can modify based on your needs.
        template_content = load_template(template_name)
        filled_content = fill_template(template_content, {})
        save_pipeline(filled_content)

if __name__ == '__main__':
    main()
