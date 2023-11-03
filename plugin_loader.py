"""
-----------------This Code is written by-----------------
---------------------Abhinav Singla----------------------
"""

#Code Starts Here

# To load all the plugins

import importlib
import os

def load_plugins():
    plugins = {}
    plugin_dir = 'plugins'

    for filename in os.listdir(plugin_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            plugin_name = os.path.splitext(filename)[0]
            module = importlib.import_module(f'{plugin_dir}.{plugin_name}')
            plugins[plugin_name] = module

    return plugins
