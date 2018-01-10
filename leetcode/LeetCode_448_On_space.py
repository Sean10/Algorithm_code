class Solution:
    def findDisappearedNumbers(self, nums):
        """
        :type nums: List[int]
        :rtype: List[int]
        """
        for i,x in enumerate(nums):
            index = abs(nums[i]) - 1
            nums[index] = -nums[index] if nums[index] > 0 else nums[index]

        ans = []
        for i,x in enumerate(nums):
            if nums[i] > 0:
                ans.append(i+1)
        return ans
