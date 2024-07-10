import graphviz

def create_visualization(data):
    dot = graphviz.Digraph()

    departments = {}
    designations = {}
    roles = {}

    for item in data:
        department = item['department']
        designation = item['designation']
        role = item['role']
        children = item['children']

        if department not in departments:
            dot.node(department, department, shape='box')
            departments[department] = department

        designation_node = f"{department}_{designation}"
        if designation_node not in designations:
            dot.node(designation_node, designation, shape='ellipse')
            dot.edge(department, designation_node)
            designations[designation_node] = designation_node

        role_node = f"{designation_node}_{role}"
        if role_node not in roles:
            dot.node(role_node, role, shape='plaintext')
            dot.edge(designation_node, role_node)
            roles[role_node] = role_node

        for child_designation in children:
                    child_node = f"{department}_{child_designation}"
                    if child_node not in designations:
                        dot.node(child_node, child_designation, shape='ellipse')
                        designations[child_node] = child_node
                    dot.edge(role_node, child_node)

    return dot


