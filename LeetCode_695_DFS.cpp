class Solution {
public:
    int maxAreaOfIsland(vector<vector<int>>& grid) {
        this->grid = grid;
        flag.resize(grid.size());
        for(int i = 0;i < grid.size();i++)
            flag[i].resize(grid[0].size());

        int ans = 0;
        for(int i = 0; i < grid.size(); i++)
        {
            for(int j = 0;j < grid[0].size();j++)
            {
                ans = max(ans, area(i,j));
            }
        }
        return ans;

    }

    int area(int r, int c) {
        if (r < 0 || r >= grid.size() || c < 0 || c >= grid[0].size() || flag[r][c] != 0 || grid[r][c] == 0)
             return 0;
        flag[r][c] = 1;
        return (1 + area(r+1,c) + area(r-1, c) + area(r, c-1) + area(r,c+1));
    }

private:
    vector<vector<int>> grid;
    vector<vector<int>> flag;
};
