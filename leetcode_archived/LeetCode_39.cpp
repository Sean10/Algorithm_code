class Solution {
public:
    vector<vector<int>> combinationSum(vector<int>& candidates, int target) {
        vector<vector<int>> ans;
        helper(candidates, {},target, ans, 0);
        return ans;
    }

    void helper(vector<int>& candidates, vector<int> temp,int target, vector<vector<int>>& ans, int start)
    {
        if(sum(temp) == target)
        {
            ans.push_back(temp);
            return ;
        }else if(sum(temp) > target)
            return ;

        for(int i = start;i < candidates.size(); i++)
        {
            temp.push_back(candidates[i]);
            helper(candidates, temp, target, ans,i);
            temp.pop_back();
        }
    }

    int sum(vector<int> candidates)
    {
        int cnt = 0;
        for(auto i = candidates.begin(); i != candidates.end(); i++)
            cnt += *i;
        return cnt;
    }
};
