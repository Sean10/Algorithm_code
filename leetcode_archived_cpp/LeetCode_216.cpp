class Solution {
public:
    vector<vector<int>> combinationSum3(int k, int n) {
        vector<vector<int>> ans;
        helper(ans, {}, k, n);
        return ans;
    }

    void helper(vector<vector<int>> &ans, set<int> temp, int k, int n)
    {
        if(k == 0 && n == 0)
        {
            vector<int> news;
            news.assign(temp.begin(), temp.end());
            ans.push_back(news);
        }
        if(k < 1 || n < 1)
            return ;

        for(int i = 1; i <= 9; i++)
        {
            if(temp.find(i) != temp.end())
                return ;
            temp.insert(i);
            helper(ans, temp, k-1, n-i);
            temp.erase(i);
        }
    }
};
