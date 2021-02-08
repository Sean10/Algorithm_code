class Solution {
public:
    vector<vector<int>> fourSum(vector<int>& nums, int target) {
        vector<vector<int>> ans;
        int n = nums.size();
        if(n < 4)
            return ans;
        sort(nums.begin(), nums.end());
        for(int i = 0 ;i < n-3;i++)
        {
            if(i > 0 && nums[i] == nums[i-1]) continue;
            // if(nums[i]+nums[i+1]+nums[i+2]=nums[i+3] < target) continue;
            // if(nums[i]+nums[i+1]+nums[i+2]=nums[i+3] > target) break;
            for(int j = i+1; j < n- 2;j++)
            {
                if(j > i+1 && nums[j] == nums[j-1]) continue;
                int k = j+1, l = n-1;
                while(k < l)
                {
                    if(k > j+1 && nums[k] == nums[k-1])
                    {
                        k++;
                        continue;
                    }
                    if(l < n-1 && nums[l] == nums[l+1])
                    {
                        l--;
                        continue;
                    }
                    int temp = nums[i]+nums[j]+nums[k]+nums[l];
                    if(temp < target) k++;
                    else if(temp > target) l--;
                    else
                    {
                        ans.push_back(vector<int>{nums[i],nums[j],nums[k],nums[l]});
                        k++;
                    }
                }
            }
        }
        return ans;
    }
};
