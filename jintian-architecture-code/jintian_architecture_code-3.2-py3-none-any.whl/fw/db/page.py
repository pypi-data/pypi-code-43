class PageUtils(object):
    def __init__(self, start: int, pageSize: int, totalCount: int, data: list):
        self.start = start
        self.pageSize = pageSize
        self.totalCount = totalCount
        self.list = data

        if (self.totalCount % self.pageSize == 0):
            self.totalPageCount = self.totalCount // self.pageSize;
        else:
            self.totalPageCount = self.totalCount // self.pageSize + 1;

        self.currentPageNo = self.start // self.pageSize + 1;
        self.hasNextPage = self.currentPageNo < self.totalPageCount;
        self.hasPreviousPage = self.currentPageNo > 1;
        self.isStartPage = self.currentPageNo == 1;
        self.isEndPage = self.currentPageNo == self.totalPageCount;
