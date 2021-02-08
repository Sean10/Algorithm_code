class Solution {
public:
    vector<int> spiralOrder(vector<vector<int>>& matrix) {
        if (matrix.empty() || matrix[0].empty())
            return {};
        vector<vector<int>> dir{{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
        int m = matrix.size(), n = matrix[0].size();

        vector<int> step{n, m-1};
        int idir = 0;
        int row = 0, col = -1;

        vector<int> ans;
        while(step[idir%2])
        {
            for (int i = 0;i < step[idir%2]; i++)
            {
                row += dir[idir][0];
                col += dir[idir][1];
                ans.push_back(matrix[row][col]);
            }
            step[idir%2]--;
            idir = (idir+1)%4;
        }

        return ans;
    }
};
