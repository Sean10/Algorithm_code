class Solution {
public:
    int findShortestSubArray(vector<int>& nums) {
        int len = nums.size();
        int max_num = *max_element(nums.begin(),nums.end()) + 1;
        vector<int> max_(max_num, 0);
        vector<int> min_(max_num, 0x7FFFFFFF);
        vector<int> cnt_(max_num,0);


        for(int i = 0;i < len;i++)
        {
            max_[nums[i]] = max(max_[nums[i]], i);
            min_[nums[i]] = min(min_[nums[i]], i);
            cnt_[nums[i]]++;
        }

        int degree = *max_element(cnt_.begin(),cnt_.end());
        int ans = len;
        for(int i = 0;i < len;i++)
        {
            if(cnt_[nums[i]] == degree)
            {
                ans = min(ans, max_[nums[i]] - min_[nums[i]] + 1);
            }
        }
        return ans;
    }
};
