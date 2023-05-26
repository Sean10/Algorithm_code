class Solution:
    def findShortestSubArray(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        max_ = {}
        min_ = {}
        cnt_ = collections.defaultdict(int)


        for key, val in enumerate(nums):
            max_[val] = max(max_.get(val,-1), key)
            min_[val] = min(min_.get(val,0x7FFFFFFF),key)
            cnt_[val] += 1

        degree = max(cnt_.values())
        ans = len(nums)

        for val in nums:
            if cnt_[val] == degree:
                ans = min(ans, max_[val] - min_[val] +1)
        return ans
