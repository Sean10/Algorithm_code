class Solution {
public:
    vector<vector<int>> combinationSum2(vector<int>& candidates, int target) {
        vector<vector<int>> ans;
        set<vector<int>> temp;
        sort(candidates.begin(), candidates.end());
        helper(candidates, {},target, temp, 0);
        ans.assign(temp.begin(),temp.end());
        return ans;
    }

    void helper(vector<int>& candidates, vector<int> temp,int target, set<vector<int>>& ans, int start)
    {
        if(sum(temp) == target)
        {
            ans.insert(temp);
            return ;
        }else if(sum(temp) > target)
            return ;

        for(int i = start;i < candidates.size(); i++)
        {
            temp.push_back(candidates[i]);
            helper(candidates, temp, target, ans,i+1);
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
