class Solution {
public:
    vector<int> findDiagonalOrder(vector<vector<int>>& matrix) {
        if (matrix.empty() || matrix[0].empty())
            return {};
        int m = matrix.size(), n = matrix[0].size();

        vector<int> ans;
        for (int i = 0;i < m+n-1; i++)
        {
            int begin_size = ans.size();
            for (int row = max(0, i-n+1), col = min(i, n-1);row < m && col >= 0;row++, col--)
                ans.push_back(matrix[row][col]);
            if (i%2 == 0)
                reverse(ans.begin()+begin_size, ans.end());
        }
        return ans;
    }
};
