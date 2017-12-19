class Solution {
public:
    int minSubArrayLen(int s, vector<int>& nums) {
        int temp_sum = 0,start = 0, min_len = INT_MAX;
        for(int i = 0; i < nums.size() ;i++)
        {
            temp_sum += nums[i];
            while(temp_sum >= s)
            {
                min_len = min(min_len, i-start +1);
                temp_sum -= nums[start++];
            }
        }
        return min_len == INT_MAX ? 0 : min_len;
    }
};
