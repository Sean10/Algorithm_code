class Solution {
public:
    int lengthOfLIS(vector<int>& nums) {
        int len = nums.size();
        if(len == 0)
            return 0;
        vector<int> dp(len,1);
        int max_ = dp[0];
        for(int i = 0; i < len;i++)
        {
            for(int j = 0;j < i;j++)
                if(nums[i] > nums[j] && dp[i] < dp[j]+1)
                    dp[i] = dp[j]+1;
            max_ = max(max_, dp[i]);
        }


        return max_;
    }
};
