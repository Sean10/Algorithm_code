class Solution {
public:
    vector<vector<int>> permuteUnique(vector<int>& nums) {
        vector<vector<int>> ans;
        sort(nums.begin(), nums.end());
        helper(nums, {}, ans, vector<bool>(nums.size()));
        return ans;
    }

    void helper(vector<int>& nums, vector<int> temp, vector<vector<int>> &ans, vector<bool> flag)
    {
        if(temp.size() == nums.size()){
            ans.push_back(temp);
            return ;
        }

        for(int i = 0;i < nums.size(); i++)
        {
            if(flag[i] || i > 0 && nums[i] == nums[i-1] && flag[i-1])
                continue;
            flag[i] = true;
            temp.push_back(nums[i]);
            helper(nums, temp, ans, flag);
            temp.pop_back();
            flag[i] = false;
        }
    }
};
