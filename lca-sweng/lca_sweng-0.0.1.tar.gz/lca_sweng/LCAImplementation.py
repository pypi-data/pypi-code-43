#!/usr/bin/python
# create a Node class for the binary tree


class TreeNode:
    def __init__(self, data):
        self.left = None
        self.right = None
        self.data = data


# LCA class


class LCA:
    def __init__(self):
        self.size = 0
        self.root = None

############# isEmpty() ###################

    # return if the tree is empty namely size is 0

    def isempty(self):
        return self.root is None

############# sizeOf() ###################

    # return size of tree

    def __size__(self):
        return self.size


############# INSERT ###################

    # returns true if insert data successfully, otherwise false


    def insert(self, data):
        if data is None or type(data) is not int:
            return False
        elif self.root is None:
            self.root = TreeNode(data)
            self.size += 1
            return True
        else:
            self.__insert(self.root, data)
            return True

    def __insert(self, node, data):
        if node.data:
            if node.data > data:
                if node.left is None:
                    node.left = TreeNode(data)
                    self.size += 1
                else:
                    self.__insert(node.left, data)
            elif node.data < data:
                if node.right is None:
                    node.right = TreeNode(data)
                    self.size += 1
                else:
                    self.__insert(node.right, data)
        else:
            node.data = data

############# findLCA(A,B) ###################

    def findlca(self, a, b):
        if self.isempty():
            return False

        if type(a) is not int or type(b) is not int:
            return False

        # To store paths to a and b from the root'
        path1 = []
        path2 = []

        # Find paths from root to a and root to b.'
        # If a or b is not present return -1'
        if not self.__findpath(self.root, path1, a) or not self.__findpath(self.root, path2, b):
            return -1

        # Compare the paths to get the first different value'
        i = 0
        while i < len(path1) and i < len(path2):
            if path1[i] != path2[i]:
                break
            i += 1
        return path1[i - 1]

############# findPath() ###################

    def __findpath(self, node, path, k):
        if node is None:
            return False

        path.append(node.data)

        if node.data == k:
            return True

        if (node.left is not None and self.__findpath(node.left, path, k)) or \
                (node.right is not None and self.__findpath(node.right, path, k)):
            return True

        path.pop()
        return False

def motivate_me():
    print("you are doing great, keep it up")