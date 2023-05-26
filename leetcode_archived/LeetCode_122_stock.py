class Solution:
    def maxProfit(self, prices):
        """
        :type prices: List[int]
        :rtype: int
        """
        if len(prices) <= 1:
            return 0
        ans = 0
        for key in range(1, len(prices)):
            ans += prices[key] - prices[key-1] if prices[key]-prices[key-1]>0 else 0
        return ans
            
