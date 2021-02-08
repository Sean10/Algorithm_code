# Method 1
# class Solution:
#     def matrixReshape(self, nums, r, c):
#         """
#         :type nums: List[List[int]]
#         :type r: int
#         :type c: int
#         :rtype: List[List[int]]
#         """
#         if (len(nums[0])*len(nums)) != r*c:
#             return nums
#          #tmp = [[None] * c for i in range(r)]
#         tmp = []
#         tmp_col = []
#         count = 0
#         for i in nums:
#             for j in i:
#                 tmp_col.append(j)
#                 count += 1
#                 if count == c:
#                     count = 0
#                     tmp.append(tmp_col)
#                     tmp_col = []
#         return tmp

# Method 2
# import numpy as np
# class Solution:
#     def matrixReshape(self, nums, r, c):
#         """
#         :type nums: List[List[int]]
#         :type r: int
#         :type c: int
#         :rtype: List[List[int]]
#         """
#         try:
#             return np.reshape(nums,(r,c)).tolist()
#         except:
#             return nums

# Method 3
# bug: list out of range……
