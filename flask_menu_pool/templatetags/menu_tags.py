from flask import request, current_app, _request_ctx_stack
from jinja2 import contextfunction

def cut_after(node, levels, removed):
    """
    given a tree of nodes cuts after N levels
    """
    if levels == 0:
        removed.extend(node.children)
        node.children = []
    else:
        removed_local = []
        for n in node.children:
            if n.visible:
                cut_after(n, levels - 1, removed)
            else:
                removed_local.append(n)
        for n in removed_local:
            node.children.remove(n)
        removed.extend(removed_local)


def remove(node, removed):
    removed.append(node)
    if node.parent:
        if node in node.parent.children:
            node.parent.children.remove(node)

def cut_levels(nodes, from_level, to_level, extra_inactive, extra_active):
    """
    cutting nodes away from menus
    """
    final = []
    removed = []
    selected = None
    for node in nodes: 
        if not hasattr(node, 'level'):
            # remove and ignore nodes that don't have level information
            remove(node, removed)
            continue
        if node.level == from_level:
            # turn nodes that are on from_level into root nodes
            final.append(node)
            node.parent = None
        if not node.ancestor and not node.selected and not node.descendant:
            # cut inactive nodes to extra_inactive, but not of descendants of 
            # the selected node
            cut_after(node, extra_inactive, removed)
        if node.level > to_level and node.parent:
            # remove nodes that are too deep, but not nodes that are on 
            # from_level (local root nodes)
            remove(node, removed)
        if node.selected:
            selected = node
        if not node.visible:
            remove(node, removed)
    if selected:
        cut_after(selected, extra_active, removed)
    if removed:
        for node in removed:
            if node in final:
                final.remove(node)
    return final

@contextfunction    
def menu_tag(context, namespace="main", from_level=0, to_level=100, extra_inactive=100, extra_active=100, template = "menu.html", next_page = None, **extra_context): 
    app = current_app
    menu_pool = app.extensions['menu_pool']
    if next_page:
                children = next_page.children
    else:
        nodes = menu_pool.get_nodes(namespace)
        children = cut_levels(nodes, from_level, to_level, extra_inactive, extra_active)
    context  = {'children':children,
                'template':template,
                'from_level':from_level,
                'to_level':to_level,
                'extra_inactive':extra_inactive,
                'extra_active':extra_active,
                'namespace':namespace}
    app.update_template_context(context)
    t = app.jinja_env.get_template(template) 
    return t.render(context) 

@contextfunction    
def breadcrumb_tag(context, namespace="main", start_level = 0 , template = "breadcrumb.html"): 
    app = current_app
    menu_pool = app.extensions['menu_pool']
    ancestors = []
    nodes = menu_pool.get_nodes(namespace)
    selected = None
    home = None
    for node in nodes:
        if node.selected:
            selected = node
        if node.get_absolute_url() == "/":
            home = node
    if selected and selected != home:
        n = selected
        while n:
            if n.visible or not only_visible:
                ancestors.append(n)
            n = n.parent
    if not ancestors or (ancestors and ancestors[-1] != home) and home:
        ancestors.append(home)
        ancestors.reverse()
        if len(ancestors) >= start_level:
           ancestors = ancestors[start_level:]
        else:
           ancestors = []
    context  = {'ancestors':ancestors,
               'template': template}
    t = app.jinja_env.get_template(template) 
    return t.render(context) 