import os
import sys

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(LOCAL_DIR))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from widget.ui.object_tree import ObjectTree
from util.widget import find_widget_parent_instance


def get_event_node(event):
    tree = get_event_tree(event)
    return tree.get_node() if tree is not None else None


def get_event_tree(event):
    widget = event.widget
    tree = find_widget_parent_instance(widget, ObjectTree)
    return tree
