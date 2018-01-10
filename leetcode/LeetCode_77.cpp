class Solution {
public:
    vector<vector<int>> combine(int n, int k) {
        vector<vector<int>> ans;
        //set<vector<int>> temp;
        helper(n, k, {}, ans,1);
        return ans;
    }

    void helper(int n, int k, vector<int> temp, vector<vector<int>>& ans, int start)
    {
        if(temp.size() == k)
        {
            ans.push_back(temp);
            return ;
        }

        for(int i = start;i <= n; i++)
        {
            if(find(temp.begin(), temp.end(), i) != temp.end())
                continue;
            temp.push_back(i);
            helper(n, k, temp, ans,i+1);
            temp.pop_back();
        }
    }
};
