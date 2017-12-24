class Solution {
public:
    int dominantIndex(vector<int>& nums) {
        int n = nums.size();
        if(n == 1)
            return 0;

        //sort(nums.begin(), nums.end())
        int max_num = nums[0];
        int max_pos = 0;
        int pre_max = 0;
        for(int i = 1;i < n; i++)
        {
            if(max_num < nums[i])
            {
                pre_max = max_num;
                max_num = nums[i];
                max_pos = i;
            }
            else if(pre_max < nums[i])
                pre_max = nums[i];
        }

        if(pre_max != 0 && max_num / pre_max < 2)
            return -1;
        return max_pos;
    }
};
