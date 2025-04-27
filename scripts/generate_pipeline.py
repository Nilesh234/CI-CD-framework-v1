import yaml
import json
import os
import shutil

# Constants
BLUEPRINT_YAML = "blueprint/pipeline-blueprint.yaml"
BLUEPRINT_JSON = "blueprint/pipeline-blueprint.json"
OUTPUT_PIPELINE_FILE = ".github/workflows/generated-pipeline.yml"
TEMPLATE_FOLDER = "templates/"

def load_blueprint():
    if os.path.exists(BLUEPRINT_YAML):
        with open(BLUEPRINT_YAML, "r") as file:
            return yaml.safe_load(file)
    elif os.path.exists(BLUEPRINT_JSON):
        with open(BLUEPRINT_JSON, "r") as file:
            return json.load(file)
    else:
        raise Exception("No blueprint file found!")

def copy_template(technology):
    template_path = os.path.join(TEMPLATE_FOLDER, f"{technology}-template.yml")
    if not os.path.exists(template_path):
        raise Exception(f"No template found for technology: {technology}")
    shutil.copy(template_path, OUTPUT_PIPELINE_FILE)

def customize_pipeline(blueprint):
    with open(OUTPUT_PIPELINE_FILE, "r") as file:
        content = file.read()
    customized = content.replace("PROJECT_NAME", blueprint.get("project_name", "project"))
    branches = blueprint.get("branching", {}).get("allowed_branches", [])
    branch_placeholder = "\n      - " + "\n      - ".join(branches)
    customized = customized.replace("BRANCHES_PLACEHOLDER", branch_placeholder)
    deploy_method = blueprint.get("deployment_target", {}).get("deployment_method", "terraform")
    customized = customized.replace("DEPLOY_METHOD", deploy_method)
    with open(OUTPUT_PIPELINE_FILE, "w") as file:
        file.write(customized)

def main():
    blueprint = load_blueprint()
    copy_template(blueprint["technology"])
    customize_pipeline(blueprint)
    print("Pipeline generated successfully from blueprint.")

if __name__ == "__main__":
    main()
