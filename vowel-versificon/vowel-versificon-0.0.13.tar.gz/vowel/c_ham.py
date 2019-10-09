Ans="""class graph():
    def __init__(self,vertices):
        self.graph=[[0 for column in range(vertices)]\
                    for row in range(vertices)]
        self.V=vertices
    def isSafe(self,V,pos,path):
        if self.graph[path[pos-1]][V]==0:
            return False

        for vertex in path:
            if vertex==V:
                return False
        return True
    def hamCycleUtil(self,path,pos):
        if pos==self.V:
            if self.graph[path[pos-1]][path[0]]==1:
                return True
            else:
                return False
        for V in range(1,self.V):
            if self.isSafe(V,pos,path)==True:
                path[pos]=V
                if self.hamCycleUtil(path,pos+1)==True:
                    return True
                path[pos]=-1
        return False
    def HamCycle(self):
        path=[-1]*self.V
        path[0]=0
        if self.hamCycleUtil(path,1)==False:
            print("Soln doesn't exist")
            return False
        self.printSolution(path)
        return True
    def printSolution(self,path):
        print("Solution exists: following is one hamiltionian is one cycle")
        for vertex in path:
            print(vertex,)
        print(path[0],"\n")
        
g1=graph(5)
g1.graph=[[0,1,0,1,0],[1,0,1,1,1],[0,1,0,0,1],[1,1,0,0,1],[0,1,1,1,0]]
g1.HamCycle()

g2=graph(5)
g2.graph=[[0,1,0,1,0],[1,0,1,1,1],[0,1,0,0,1],[1,1,0,0,0],[0,1,1,0,0]]
g2.HamCycle()
"""