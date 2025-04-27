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
        return None  # No blueprint found

# Load template for a given technology
def load_template(technology):
    template_file = f'{technology.lower()}-template.yml'
    template_path = os.path.join(TEMPLATES_DIR, template_file)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f'Template for {technology} not found at {template_path}')
    
    with open(template_path, 'r') as f:
        return f.read()

# Dynamic deploy commands based on deployment method
def get_deploy_commands(deployment_method):
    deployment_method = (deployment_method or 'sam').lower()
    if deployment_method == 'sam':
        return "sam build && sam deploy --no-confirm-changeset"
    elif deployment_method == 'terraform':
        return "terraform init && terraform apply -auto-approve"
    elif deployment_method == 'docker':
        return "docker build -t myapp . && docker push myapp"
    elif deployment_method == 'cdk':
        return "cdk deploy --require-approval never"
    elif deployment_method == 'cloudformation':
        return "aws cloudformation deploy --template-file template.yaml --stack-name my-stack"
    else:
        return f"echo 'Unsupported deployment method: {deployment_method}'"

# Replace placeholders in the template with values from the blueprint
def fill_template(template_content, blueprint):
    deployment_method = blueprint.get('deployment_target', {}).get('deployment_method', 'sam') if blueprint else 'sam'
    deploy_commands = get_deploy_commands(deployment_method)
    
    replacements = {
        'PROJECT_NAME': blueprint.get('project_name', 'MyProject'),
        'BRANCHES_PLACEHOLDER': yaml.dump(blueprint.get('branching', {}).get('allowed_branches', ['main'])).strip() if blueprint else '["main"]',
        'DEPLOY_COMMANDS': deploy_commands,
        'BUILD_TYPE': blueprint.get('build_type', 'full'),
        'LINT_STAGE': str(blueprint.get('stages', {}).get('lint', False)).lower(),
        'STATIC_ANALYSIS_STAGE': str(blueprint.get('stages', {}).get('static_analysis', False)).lower(),
        'UNIT_TESTS_STAGE': str(blueprint.get('stages', {}).get('unit_tests', False)).lower(),
        'INTEGRATION_TESTS_STAGE': str(blueprint.get('stages', {}).get('integration_tests', False)).lower(),
        'SECURITY_SCAN_STAGE': str(blueprint.get('stages', {}).get('security_scan', False)).lower(),
        'PACKAGE_ARTIFACT_STAGE': str(blueprint.get('stages', {}).get('package_artifact', False)).lower(),
        'DEPLOY_STAGE': str(blueprint.get('stages', {}).get('deploy', False)).lower(),
        'CLOUD_PROVIDER': blueprint.get('deployment_target', {}).get('cloud_provider', 'aws'),
        'REGION': blueprint.get('deployment_target', {}).get('region', 'us-east-1'),
        'SERVICE': blueprint.get('deployment_target', {}).get('service', 'lambda'),
        'ENVIRONMENT': blueprint.get('deployment_target', {}).get('environment', 'dev')
    }
    
    for placeholder, value in replacements.items():
        template_content = template_content.replace(placeholder, str(value))

    return template_content

# Save the final pipeline with a timestamp in a separate folder
def save_pipeline(content):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"generated-pipeline_{timestamp}.yml"
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"Pipeline generated successfully at: {output_path}")

# Main flow
def main():
    blueprint = load_blueprint()

    if blueprint:
        print("Blueprint detected: Generating pipeline from blueprint...")
        technology = blueprint.get('technology', 'python')  # default to python if missing
    else:
        print("No blueprint found: Generating pipeline from default template...")
        technology = 'python'  # fallback template

    template_content = load_template(technology)
    filled_content = fill_template(template_content, blueprint or {})
    save_pipeline(filled_content)

if __name__ == '__main__':
    main()
