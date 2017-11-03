class Solution:
    def maxAreaOfIsland(self, grid):
        """
        :type grid: List[List[int]]
        :rtype: int
        """
        # flag = [[0 for i in range(len(grid[0]))] for j in range(len(grid))]
        ans = 0
        flag = set()

        def area(r, c):
            if r not in range(len(grid)) or c not in range(len(grid[0])) or (r,c) in flag or not grid[r][c]:
                return 0
            flag.add((r,c))
            return 1 + area(r-1,c) + area(r+1,c) + area(r, c-1) + area(r, c+1)

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                ans = max(ans, area(i,j))
        return ans
