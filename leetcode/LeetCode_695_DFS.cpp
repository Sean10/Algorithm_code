// class Solution {
// public:
//     int maxAreaOfIsland(vector<vector<int>>& grid) {
//         this->grid = grid;
//         flag.resize(grid.size());
//         for(int i = 0;i < grid.size();i++)
//             flag[i].resize(grid[0].size());
//
//         int ans = 0;
//         for(int i = 0; i < grid.size(); i++)
//         {
//             for(int j = 0;j < grid[0].size();j++)
//             {
//                 ans = max(ans, area(i,j));
//             }
//         }
//         return ans;
//
//     }
//
//     int area(int r, int c) {
//         if (r < 0 || r >= grid.size() || c < 0 || c >= grid[0].size() || flag[r][c] != 0 || grid[r][c] == 0)
//              return 0;
//         flag[r][c] = 1;
//         return (1 + area(r+1,c) + area(r-1, c) + area(r, c-1) + area(r,c+1));
//     }
//
// private:
//     vector<vector<int>> grid;
//     vector<vector<int>> flag;
// };

// DFS iterator
 class Solution {
public:
    int maxAreaOfIsland(vector<vector<int>>& grid) {
        int ans = 0;
        //vector<vector<int>> flag(grid.size(), vector<int>(grid[0].size(), 0));
        int flag[50][50] = {0};
        int dir_x[] = {-1,1,0,0};
        int dir_y[] = {0, 0, -1, 1};

        for(int i = 0;i < grid.size(); i++)
        {
            for(int j = 0;j < grid[0].size();j++)
            {
                if(grid[i][j] && !flag[i][j])
                {
                    int tmp_ans = 0;
                    stack<pair<int,int>> Stack_;
                    Stack_.push({i,j});
                    flag[i][j] = 1;
                    while(!Stack_.empty())
                    {
                        pair<int, int> tmp_vec;
                        tmp_vec = Stack_.top();
                        Stack_.pop();
                        int r = tmp_vec.first;
                        int c = tmp_vec.second;
                        tmp_ans++;

                        for(int x = 0; x < 4;x++)
                        {
                            int nr = r + dir_x[x];
                            int nc = c + dir_y[x];
                            if(nr >= 0 && nr < grid.size() && nc >= 0 && nc < grid[0].size() && flag[nr][nc] == 0 && grid[nr][nc] == 1)
                            {

                                Stack_.push({nr,nc});
                                flag[nr][nc] = 1;
                            }
                        }


                    }
                    ans = max(tmp_ans,ans);
                }
            }
        }
        return ans;

    }

};
