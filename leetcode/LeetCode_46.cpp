class Solution {
public:
    vector<vector<int>> permute(vector<int>& nums) {
        vector<vector<int>> ans;
        helper(nums, {},ans);
        return ans;
    }

    void helper(vector<int>& nums, vector<int> temp, vector<vector<int>>& ans)
    {
        if(temp.size() == nums.size())
            ans.push_back(temp);

        for(int i = 0;i < nums.size(); i++)
        {
            if(find(temp.begin(), temp.end(), nums[i]) != temp.end())
                continue;
            temp.push_back(nums[i]);
            helper(nums, temp, ans);
            temp.pop_back();
        }
    }
};
