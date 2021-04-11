

import treelib



# 来自[What is the most efficient way to get all nodes in a certain depth · Issue \#147 · caesar0301/treelib](https://github.com/caesar0301/treelib/issues/147)
# 只是主要代码的样例
def level_traverse():
    crush_tree = treelib.Tree()
    for i in range(crush_tree.depth(), -1, -1):
        print(list(crush_tree.filter_nodes(func=lambda x: crush_tree.depth(x) == i)))

# 找父母
def level_traverse_with_parent():
    for i in range(crush_tree.depth(), -1, -1):
        print(list(crush_tree.filter_nodes(func=lambda x: crush_tree.depth(x) == i)))


