class Solution {
public:
    int rob(vector<int>& nums) {
        if(nums.size() < 1)
            return 0;

        vector<int> ans(nums.size(), 0);

        for(int i = 0;i < nums.size(); i++)
        {
            if(i >= 2)
                ans[i] = max(ans[i-2]+ nums[i], ans[i-1]);
            else if(i == 0)
                ans[i] = nums[i];
            else
                ans[i] = max(nums[i], ans[0]);

        }
        return ans[nums.size()-1];
    }
};
