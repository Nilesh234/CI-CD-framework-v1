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

# Load template
def load_template(language):
    template_file = f'{language.lower()}-template.yml'
    template_path = os.path.join(TEMPLATES_DIR, template_file)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f'Template for {language} not found at {template_path}')
    
    with open(template_path, 'r') as f:
        return f.read()

# Replace placeholders
def fill_template(template_content, blueprint):
    replacements = {
        'PROJECT_NAME': blueprint.get('project_name', 'MyProject'),
        'BRANCHES_PLACEHOLDER': str(blueprint.get('branches', ['main'])),
        'DEPLOY_METHOD': blueprint.get('deploy_method', 'sam')
    }
    
    for placeholder, value in replacements.items():
        if isinstance(value, list):
            # YAML expects a list like ["main", "dev"]
            value = str(value).replace("'", '"')
        template_content = template_content.replace(placeholder, str(value))
    
    return template_content

# Save final pipeline with timestamp
def save_pipeline(content):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}.yml"
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"Pipeline generated successfully at {output_path}")

# Main flow
def main():
    blueprint = load_blueprint()
    language = blueprint.get('language', 'python')  # default to python
    template_content = load_template(language)
    filled_content = fill_template(template_content, blueprint)
    save_pipeline(filled_content)

if __name__ == '__main__':
    main()
