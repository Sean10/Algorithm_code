class Solution {
public:
    vector<vector<int>> threeSum(vector<int>& nums) {
        int n = nums.size();
        vector<vector<int>> ans;
        if(n < 3)
            return ans;
        sort(nums.begin(), nums.end());
        for(int i = 0;i < n-2; i++)
        {
            if(i > 0 && nums[i] == nums[i-1]) continue;
            int j = i+1, k = n-1;
            while(j < k)
            {
                if(j > i+1 && nums[j] == nums[j-1])
                {
                    j++;
                    continue;
                }
                if(k < n-1 && nums[k] == nums[k+1])
                {
                    k--;
                    continue;
                }
                int temp = nums[i]+nums[j]+nums[k];
                if(temp < 0) j++;
                else if(temp > 0) k--;
                else
                {
                    //cout << nums[i] << nums[j] << nums[k];
                    ans.push_back(vector<int>{nums[i],nums[j],nums[k]});
                    j++;
                }

            }
        }
        return ans;
    }
};
