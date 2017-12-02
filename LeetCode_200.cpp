class Solution {
public:
    int numIslands(vector<vector<char>>& grid) {
        int rows = grid.size();
        if(rows == 0)
            return 0;
        int cols = grid[0].size();
        vector<vector<int>> flag(rows, vector<int>(cols));
        int dir_x[] = {-1,0,0,1};
        int dir_y[] = {0,-1,1,0};
        queue<pair<int,int>> q;

        int cnt = 0;
        for(int tmp_i = 0; tmp_i < rows; tmp_i ++)
        {
            for(int tmp_j = 0; tmp_j < cols; tmp_j ++)
            {
                if(grid[tmp_i][tmp_j] == '1')
                    if(flag[tmp_i][tmp_j] == 1)
                        continue;
                    else{
                        cnt += 1;
                        q.push(make_pair(tmp_i,tmp_j));
                        flag[tmp_i][tmp_j] = 1;
                        while(!q.empty())
                        {
                            int x = q.front().first;
                            int y = q.front().second;
                            q.pop();
                            for(int i = 0;i < 4;i ++)
                            {
                                int nx = x + dir_x[i];
                                int ny = y + dir_y[i];
                                if(nx >= 0 && nx < rows && ny >= 0 && ny < cols && grid[nx][ny] == '1' && flag[nx][ny] == 0)
                                {
                                    flag[nx][ny] = 1;
                                    q.push(make_pair(nx,ny));
                                }
                            }

                        }
                    }

            }
        }
        return cnt;

    }
};
