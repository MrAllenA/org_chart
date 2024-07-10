from parser import parse_custom_markdown
from render import create_visualization
markdown_text = """
# Department: Engineering
## Designation: Senior Engineer
- Role: Lead Projects
- Role: Mentor Junior Engineers

## Designation: Junior Engineer
- Role: Assist in Projects
- Role: Learn and Develop Skills

# Department: HR
## Designation: HR Manager
- Role: Manage Recruitment
- Role: Oversee Employee Relations
- Child: Junior Engineer
"""

parsed_data = parse_custom_markdown(markdown_text)
print(parsed_data)
dot = create_visualization(parsed_data)
dot.render('organization_structure', format='png', view=True)