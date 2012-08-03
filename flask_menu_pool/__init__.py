from exceptions import NamespaceAllreadyRegistered
from base import Menu, YAMLMenu
from templatetags.menu_tags import menu_tag, breadcrumb_tag
import copy
import yaml
import os
from os.path import join
from flask import _request_ctx_stack, request, current_app, Blueprint

class MenuPool(object):

    blueprint = Blueprint('menu_pool_blueprint', __name__, template_folder='templates')
    
    
    def __init__(self, app):
        app.config.setdefault('MENUPOOL_ENCODING', 'utf8')
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        app.jinja_env.globals['menu']       = menu_tag
        app.jinja_env.globals['breadcrumb'] = breadcrumb_tag
        app.extensions['menu_pool']         = self
        self.menus = {}
        self._file_cache = {}

    @property
    def root(self):
        """Full path to the directory where pages are looked for.

        It is the `FLATPAGES_ROOT` config value, interpreted as relative to
        the app root directory.
        """
        return join(self.app.root_path, self.app.config['MENUPOOL_ROOT'])
    
    #Stub
    def clear(self, site_id=None, language=None, all=False):
        '''
        This invalidates the cache for a given menu (site_id and language)
        '''
        cache.delete_memoized('get_nodes')
    
    def register_menu(self, menu):
        if menu.namespace in self.menus.keys():
            raise NamespaceAllreadyRegistered(
                "[%s] a menu with this name is already registered" % menu.__name__)
        self.menus[menu.namespace] = menu
    
    #Stub
    def get_or_register_menu(self, menu_title, menu_file):
        site_id = current_app.config['SITE_ID']
        menu_namespace = "%s-%s"%(site_id,menu_title)
        if menu_namespace in self.menus.keys():
            return self.menus[menu_namespace]
        else:
            tree = yaml.load(self._load_file(self.root, menu_file))
            self.register_menu(YAMLMenu(menu_namespace, tree))
            return self.menus[menu_namespace]
    
    def _load_file(self, path, filename):
        mtime = os.path.getmtime(join(path,filename))
        cached = self._file_cache.get(filename)
        if cached and cached[1] == mtime:
            menu = cached[0]
        else:
            with open(join(path,filename)) as fd:
                menu = fd.read().decode(
                    self.app.config['MENUPOOL_ENCODING'])
            self._file_cache[filename] = menu, mtime
        return menu
    
    def get_nodes(self, menu_title=None):
        site_id = current_app.config['SITE_ID']
        menu_namespace = "%s-%s"%(site_id, menu_title)
        nodes = self._mark_selected(self.menus[menu_namespace].get_nodes())
        return nodes 

    def _mark_selected(self, nodes):
        sel = None
        for node in nodes:
            node.sibling = False
            node.ancestor = False
            node.descendant = False
            node.selected = False
            if node.get_absolute_url() == request.path[:len(node.get_absolute_url())]:
                if sel:
                    if len(node.get_absolute_url()) > len(sel.get_absolute_url()):
                        sel = node
                else:
                    sel = node
            else:
                node.selected = False
        if sel:
            sel.selected = True
            n = sel.parent
            while n:
                n.ancestor = True
                n = n.parent
            
        return nodes