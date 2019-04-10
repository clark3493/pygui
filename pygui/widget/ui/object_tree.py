import tkinter as tk

from tkinter import ttk
from uuid import uuid4


def DEFAULT_TREE_FILTER(k):
    if k.startswith('_'):
        return False
    else:
        return True


def tree_node(o, parent=None, iid=None, name=None):
    if any(isinstance(o, c) for c in (list, tuple)):
        return IterableTreeNode(o, parent, iid, name=name)
    elif isinstance(o, dict):
        return DictTreeNode(o, parent, iid, name=name)
    else:
        return TreeNode(o, parent, iid, name=name)


class ObjectTree(ttk.Treeview):

    def __init__(self, parent=None, topdict={}, columns=('Value',), tree_filter=DEFAULT_TREE_FILTER, **kwargs):
        super().__init__(parent, columns=columns, **kwargs)
        self.parent = parent
        self.topdict = topdict
        self.tree_filter = tree_filter
        self._child_nodes = []
        self._id_node_dict = {}
        self._node_id_dict = {}

        self.id = ''

        self.refresh_topdict()
        self.bind_keys()
        self.configure_ui()
        self.set_column_titles(columns)

    @property
    def child_nodes(self):
        return self._child_nodes

    @property
    def id_node_dict(self):
        return self._id_node_dict

    @property
    def node_id_dict(self):
        return {v: k for k, v in self.id_node_dict.items()}

    def bind_keys(self):
        self.bind('<<TreeviewOpen>>', self.on_open)
        self.bind('<Button-3>', self.on_right_click)

    def configure_ui(self):
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.yview)
        vsb.pack(side='right', fill='y')
        self.configure(yscrollcommand=vsb.set)

    def get_node(self, node=None, iid=None):
        node = self if node is None else node
        iid = self.focus() if iid is None else iid
        for _iid, _node in node.id_node_dict.items():
            if str(_iid) == iid:
                return _node
            else:
                subnode = self.get_node(_node, iid)
                if subnode is not None:
                    return subnode
        return None

    def on_open(self, event=None):
        node = self.get_node()
        node.on_open(event)

    def on_right_click(self, event=None):
        node = self.get_node()
        if node is not None:
            node.on_right_click(event)

    def set_column_titles(self, columns):
        for column in columns:
            self.heading(column, text=column)

    def refresh_topdict(self, d=None):
        if d is not None:
            self.topdict = d
        self._add_new_topdict_items()
        self._remove_topdict_items()

    def _add_new_topdict_items(self):
        for k, v in self.topdict.items():
            if not self._contains(k) and self.tree_filter(k):
                iid = uuid4()
                node = tree_node(v, self, iid=iid, name=k)
                self.child_nodes.append(node)
                self.insert('', tk.END, iid=iid, text=node.name.replace(" ", "-"), value=node.value.replace(" ", "-"))
                if isinstance(node, IterableTreeNode):
                    node.refresh_children()
                self.id_node_dict[iid] = node

    def _contains(self, name):
        for node in self.node_id_dict:
            if node.name == name:
                return True
        return False

    def _delete_selected_topdict_item(self, event=None):
        node = self.get_node()
        self.delete(node.iid)
        del(self.id_node_dict[node.iid])
        del(self.topdict[node.name])

    def _remove_topdict_items(self):
        for node, iid in self.node_id_dict.items():
            if node.name not in self.topdict:
                self.delete(iid)


class TreeNode(object):

    def __init__(self, obj, parent=None, iid=None, name=None):
        self.obj = obj
        self.parent = parent
        self.iid = iid
        self._name = name

        self._child_nodes = []
        self._id_node_dict = {}
        self._node_id_dict = {}

    @property
    def child_nodes(self):
        return self._child_nodes

    @property
    def id_node_dict(self):
        return self._id_node_dict

    @property
    def name(self):
        if self._name is None:
            return self.obj.__class__.__name__
        else:
            return self._name

    @property
    def node_id_dict(self):
        return {v: k for k, v in self.id_node_dict.items()}

    @property
    def value(self):
        if isinstance(self.obj, str):
            return "'" + self.obj + "'"
        else:
            return str(self.obj)

    def add_children(self, objects):
        root = self.get_tree_root()
        for o in objects:
            iid = uuid4()
            node = tree_node(o, self, iid=iid)
            self.child_nodes.append(node)
            root.insert(self.iid, tk.END, iid=iid, text=node.name.replace(" ", "-"), value=node.value.replace(" ", "-"))
            if isinstance(node, IterableTreeNode):
                node.refresh_children()
            self.id_node_dict[iid] = node

    def clear_children(self):
        root = self.get_tree_root()
        root.set_children(self.iid)

    def get_tree_root(self):
        node = self
        while not isinstance(node, ttk.Treeview):
            node = node.parent
        return node

    def on_open(self, event=None):
        self.refresh_children()

    def on_right_click(self, event=None):
        if isinstance(self.parent, ObjectTree):
            popup = _TopDictNodePopupMenu(self.parent)
            try:
                popup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                popup.grab_release()

    def refresh_children(self):
        pass


class IterableTreeNode(TreeNode):

    def __init__(self, obj, parent=None, iid=None, name=None):
        super().__init__(obj, parent, iid, name=name)

    @property
    def value(self):
        return self.obj.__class__.__name__

    def add_children(self, objects):
        root = self.get_tree_root()
        for i, o in enumerate(objects):
            iid = uuid4()
            node = tree_node(o, self, iid=iid)
            self.child_nodes.append(node)
            name = '[' + str(i) + ']'
            root.insert(self.iid, tk.END, iid=iid, text=name, value=node.value.replace(" ", "-"))
            if isinstance(node, IterableTreeNode):
                node.refresh_children()
            self.id_node_dict[iid] = node

    def refresh_children(self):
        self.clear_children()
        self.add_children(self.obj)


class DictTreeNode(IterableTreeNode):

    def __init__(self, obj, parent=None, iid=None, name=None):
        super().__init__(obj, parent, iid, name=name)

    def add_children(self, d):
        for k, v in d.items():
            iid = uuid4()
            node = tree_node(v, self, iid=iid, name=k)
            self.child_nodes.append(node)
            root = self.get_tree_root()
            root.insert(self.iid, tk.END, iid=iid, text=node.name.replace(" ", "-"), value=node.value.replace(" ", "-"))
            if isinstance(node, IterableTreeNode):
                node.refresh_children()
            self.id_node_dict[iid] = node


class _TopDictNodePopupMenu(tk.Menu):

    def __init__(self, parent, *args, tearoff=0, **kwargs):
        super().__init__(parent, *args, tearoff=tearoff, **kwargs)

        self.parent = parent

        self.add_command(label="Delete", command=self.parent._delete_selected_topdict_item)


if __name__ == "__main__":
    root = tk.Tk()
    tree = ObjectTree(root)
    tree.refresh_topdict({'a': 1, 'b': 2., 'c': 'some string',
                      'd': [[6,7],2,3,4], 'e': ('a', 'g', 't'),
                      'f': {'qwerty': 'sadf', 'z': {'p2': 1.2345}}})
    tree.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
