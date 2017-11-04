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


# Below TLE
# class Solution:
#     def maxAreaOfIsland(self, grid):
#         """
#         :type grid: List[List[int]]
#         :rtype: int
#         """
#         # flag = [[0 for i in range(len(grid[0]))] for j in range(len(grid))]
#         ans = 0
#         flag = set()
#         dir_x = [-1,1,0,0]
#         dir_y = [0, 0,-1, 1]
#
#         for i,x in enumerate(grid):
#             for j,y in enumerate(grid[0]):
#                 if grid[i][j] and (i,j) not in flag:
#                     flag.add((i,j))
#                     tmp_ans  = 0
#                     stack = [(i,j)]
#                     while stack:
#                         tmp_ans += 1
#                         r,c = stack.pop()
#                         for k in range(4):
#                             nr = r + dir_x[k]
#                             nc = c + dir_y[k]
#                             if nr in range(len(grid)) and nc in range(len(grid[0])) and (nr,nc) not in flag and grid[nr][nc]:
#                                 flag.add((i,j))
#                                 stack.append((i,j))
#                     ans = max(ans, tmp_ans)
#         return ans
