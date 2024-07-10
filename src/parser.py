import re

def parse_custom_markdown(markdown_text):
    data = []
    department = None
    designation = None
    current_roles = []
    
    for line in markdown_text.split('\n'):
        line = line.strip()
        if line.startswith("# Department:"):
            department = line.split(":", 1)[1].strip()
        elif line.startswith("## Designation:"):
            designation = line.split(":", 1)[1].strip()
            current_roles = []
        elif line.startswith("- Role:"):
            role = line.split(":", 1)[1].strip()
            current_roles.append(role)
            data.append({
                'department': department,
                'designation': designation,
                'role': role,
                'children': []
            })
        elif line.startswith("- Child:"):
            child = line.split(":", 1)[1].strip()
            if current_roles:
                for role in current_roles:
                    for item in data:
                        if item['department'] == department and item['designation'] == designation and item['role'] == role:
                            item['children'].append(child)
    
    return data


