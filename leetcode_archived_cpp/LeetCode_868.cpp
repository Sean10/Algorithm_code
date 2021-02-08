class Solution {
public:
    vector<vector<int>> transpose(vector<vector<int>>& A) {
        if (A.empty())
            return {};
        
        int m = A.size(), n = A[0].size();
        vector<vector<int>> ans(n, vector<int>(m));
        for (int i = 0; i < n; i++)
        {
            for (int j = 0;j < m;j++)
            {
                ans[i][j] = A[j][i];
            }
        }
        return ans;
    
    }
    
};
