class Solution {
public:
    int numSubarrayProductLessThanK(vector<int>& nums, int k) {
        if( k <= 1) return 0;
        int ans = 0,start = 0,sum = 1;
        for(int i = 0;i < nums.size(); i++)
        {
            sum *= nums[i];
            while(sum >= k)
            {
                sum /= nums[start++];
            }
            ans += i -start + 1;
        }


        return ans;
    }
};
