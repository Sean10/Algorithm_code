class Solution {
public:
    vector<int> productExceptSelf(vector<int>& nums) {
        int from_begin = 1, from_end = 1;
        int len = nums.size();
        vector<int> ans(len,1);
        for(int i = 0;i < nums.size(); i++)
        {
            ans[i] *= from_begin;
            from_begin *= nums[i];
            ans[len-i-1] *= from_end;
            from_end *= nums[len-i-1];
        }

        return ans;
    }
};
