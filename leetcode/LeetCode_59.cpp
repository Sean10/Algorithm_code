class Solution {
public:
    vector<vector<int>> generateMatrix(int n) {
        if (n <= 0)
            return {};
        vector<vector<int>> dir{{0, 1}, {1, 0}, {0, -1}, {-1, 0}};

        vector<vector<int>> ans;
        for (int i = 0;i < n; i++)
        {
            vector<int> temp(n, 0);
            ans.push_back(temp);
        }

        int row = 0, col = -1;
        int idir = 0;
        vector<int> step{n, n-1};
        for (int i = 1; i <= n*n;)
        {
            for (int j = 0; j < step[idir%2]; j++)
            {
                row += dir[idir][0];
                col += dir[idir][1];
                ans[row][col] = i;
                i++;
            }
            step[idir%2]--;
            idir = (idir+1)%4;
        }
        return ans;
    }
};
