class Solution:
    def moveZeroes(self, nums):
        """
        :type nums: List[int]
        :rtype: void Do not return anything, modify nums in-place instead.
        """
        j = 0
        for i,x in enumerate(nums):
            if nums[i] != 0:
                nums[j] = nums[i]
                j += 1

        while j < len(nums):
            nums[j] = 0
            j += 1
        
