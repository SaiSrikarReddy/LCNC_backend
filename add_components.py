import os
import json

# Get the name and description of the component from the user
component_name = input("Enter the name of the component you want to add: ")
component_description = input("Enter a short description for this component: ")

# Path to the components_list.json
json_path = "component_templates/components_list.json"

# Load existing data from components_list.json, if it exists
if os.path.exists(json_path):
    with open(json_path, "r") as json_file:
        components_list = json.load(json_file)
else:
    components_list = {}

# Add new component to the components_list
components_list[component_name] = component_description

# Write updated components_list back to components_list.json
with open(json_path, "w") as json_file:
    json.dump(components_list, json_file, indent=4)

# Create a new directory for the component within component_templates
new_folder_path = os.path.join("component_templates", component_name)
os.makedirs(new_folder_path, exist_ok=True)

# Create blank files within the new folder
file_names = [
    f"{component_name}.jsx", f"{component_name}_mockdata.txt",
    f"{component_name}_usage_instructions.txt"
]
for file_name in file_names:
    open(os.path.join(new_folder_path, file_name), "a").close()

print(f"Component '{component_name}' has been successfully added.")
