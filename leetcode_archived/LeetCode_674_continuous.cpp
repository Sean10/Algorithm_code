class Solution {
public:
    int findLengthOfLCIS(vector<int>& nums) {
        int len = nums.size();

        int cnt = 0;
        int max_cnt = 0;
        for(int i = 0;i < len;i++)
        {
            if(i == 0 || nums[i-1] < nums[i])
                max_cnt = max(max_cnt, ++cnt);
            else
                cnt = 1;
        }


        return max_cnt;
    }
};
