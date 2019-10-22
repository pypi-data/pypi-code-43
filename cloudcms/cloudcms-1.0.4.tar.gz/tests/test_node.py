import time
from .abstract_with_repository_test import AbstractWithRepositoryTest
from cloudcms.node import Node

class TestNode(AbstractWithRepositoryTest):
    
    @classmethod
    def setUpClass(cls):
        super(TestNode, cls).setUpClass()
        cls.branch = cls.repository.read_branch("master")

    def test_node_crud(self):
        branch = type(self).branch

        nodeObj = {
            "title": "MyNode"
        }
        node = branch.create_node(nodeObj)

        nodeRead = branch.read_node(node._doc)
        self.assertEqual(node.data, nodeRead.data)

        node.data["title"] = "New Title"
        node.update()

        nodeRead.reload()
        self.assertEqual(node.data["title"], nodeRead.data["title"])

        node.delete()
        nodeRead = branch.read_node(node._doc)
        self.assertIsNone(nodeRead)


    def test_node_query_and_find(self):
        branch = type(self).branch

        nodeObj1 = {
            "title": "Cheese burger",
            "meal": "lunch"
        }
        nodeObj2 = {
            "title": "Ham burger",
            "meal": "lunch"
        }
        nodeObj3 = {
            "title": "Turkey sandwich",
            "meal": "lunch"
        }
        nodeObj4 = {
            "title": "Oatmeal",
            "meal": "breakfast"
        }

        node1 = branch.create_node(nodeObj1)
        node2 = branch.create_node(nodeObj2)
        node3 = branch.create_node(nodeObj3)
        node4 = branch.create_node(nodeObj4)

        # Wait for nodes to index
        time.sleep(5)

        query = {
            "meal": "lunch"
        }
        queryNodes = branch.query_nodes(query)
        self.assertEqual(3, len(queryNodes))
        self.assertTrue(node1._doc in queryNodes.keys())
        self.assertTrue(node2._doc in queryNodes.keys())
        self.assertTrue(node3._doc in queryNodes.keys())

        find = {
            "search": "burger"
        }
        findNodes = branch.find_nodes(find)
        self.assertEqual(2, len(findNodes))
        self.assertTrue(node1._doc in findNodes.keys())
        self.assertTrue(node2._doc in findNodes.keys())

        node1.delete()
        node2.delete()
        node3.delete()
        node4.delete()