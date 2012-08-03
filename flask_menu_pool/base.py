# -*- coding: utf-8 -*-
import copy

class Menu(object):
    namespace = None

    def __init__(self, namespace, yaml_tree):
        self.namespace = namespace
        self.nodes = []
    
    def get_nodes(self):
        return self.nodes

class YAMLMenu(Menu):
    def __init__(self, namespace, yaml_tree):
        self.namespace = namespace
        self.yaml_tree = yaml_tree
        self.nodes = []
    
    def yaml_to_nodes(self, level=0, children = [], parent = None):
        nodes = []
        for raw_node in children:
            node = NavigationNode(raw_node.get('title'), raw_node.get('slug'), level)
            if raw_node.get('children'):
                node.children = self.yaml_to_nodes(level=(level + 1), children=raw_node.get('children'), parent=node)
            if parent != None:
                node.parent = parent
                node.ancestor = True
            self.nodes.append(node)
            nodes.append(node)
        return nodes
    
    def get_nodes(self):
        if not self.nodes:
            self.yaml_to_nodes(level=0, children=self.yaml_tree)
        return self.nodes
    
    
class NavigationNode(object):
    
    def __init__(self, title, slug, level = 0, visible=True):
        self.children = [] # do not touch
        self.parent = None # do not touch, code depends on this
        self.namespace = None # TODO: Assert why we need this and above
        self.title = title
        self.slug =  slug
        self.visible = visible
        self.level = level
        self.ancestor = False

            
    def __repr__(self):
        #return "<Navigation Node: %s>" % smart_str(self.title)
        return "<Navigation Node: %s>" % self.title
    
    def _remove_current_root(self, url):
        current_root = "/"
        if url[:len(current_root)] == current_root:
            url = url[len(current_root) - 1:]
        return url
    
    @property
    def get_slug(self):
        if self.slug != "/":
            return self.slug
        else:
            return ""
    
    @property
    def get_link(self):
        if self.slug != "/":
            return "/%s/"%self.slug
        else:
            return "/"
    
    def get_menu_title(self):
        return self.title
    
    def get_absolute_url(self):
        if self.slug != "/":
            return "/%s/"%self.slug
        else:
            return "/"

    
    def get_attribute(self, name):
        return self.attr[name]
    
    def get_descendants(self):
        nodes = []
        for node in self.children:
            nodes.append(node)
            nodes += node.get_descendants()
        return nodes

    def get_ancestors(self):
        nodes = []
        if getattr(self, 'parent', None):
            nodes.append(self.parent)
            nodes += self.parent.get_ancestors()
        return nodes
    
    
    def __unicode__(self):
        return self.title
        