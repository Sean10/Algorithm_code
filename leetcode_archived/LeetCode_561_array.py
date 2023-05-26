class Solution:
    def arrayPairSum(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        nums.sort()
        flag = True
        sum = 0
        for i in nums:
            if flag:
                sum += i
            flag = not flag
        return sum
