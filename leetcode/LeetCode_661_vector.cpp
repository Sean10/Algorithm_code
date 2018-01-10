class Solution {
public:
    vector<vector<int>> imageSmoother(vector<vector<int>>& M) {
        vector<vector<int>> dir = {{-1,-1},{-1,0},{-1,1},{0,-1},{0,1},{1,-1},{1,0},{1,1}};


        int rows = M.size();
        int cols = M[0].size();

        if(rows == 0 || cols == 0)
            return M;

        for(int i = 0;i < rows;i++)
        {
            for(int j = 0;j < cols;j++)
            {
                int tmp_ans = M[i][j];
                //cout << tmp_ans << endl;
                //cout << rows << "\t" << cols << endl;
                int cnt =1;
                for(int k = 0;k < 8;k++)
                {
                    int nr = i + dir[k][0];
                    int nc = j + dir[k][1];
                    if(nr < 0 || nr >= rows || nc < 0 || nc >= cols)
                        continue;
                    tmp_ans += M[nr][nc]&0x00FF;
                    //cout << nr << "\t" << nc << "\t" <<M[nr][nc] <<"\t"<<tmp_ans << endl;
                    cnt++;
                }

                M[i][j] |= ((tmp_ans/cnt) << 8);
            }
        }

        for(int i = 0;i < rows;i++)
            for(int j= 0;j < cols;j++)
                M[i][j] >>= 8;
        return M;
    }
};
