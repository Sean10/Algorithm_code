class Solution:
    def findMaxConsecutiveOnes(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        max_length = curr_length = 0
        for i in nums:
            if i == 1:
                curr_length += 1
            else:
                curr_length = 0
            if curr_length > max_length:
                max_length = curr_length
        return max_length
