class Solution {
public:
    int countBattleships(vector<vector<char>>& board) {
        vector<vector<int>> flag(board.size());
        for(int i = 0;i < board.size();i++)
            flag[i].assign(board[i].size(), 0);

        int cnt = 0;
        for (int i = 0;i < board.size(); i++)
            for (int j = 0;j < board[0].size(); j++)
            {
                if(flag[i][j] || board[i][j] == '.')
                    continue;
                cnt ++ ;
                for (int p = i;p < board.size() && board[p][j] == 'X'; p++)
                    flag[p][j] = 1;
                for (int p = i;p >= 0 && board[p][j] == 'X'; p--)
                    flag[p][j] = 1;
                for (int p = j;p < board[0].size() && board[i][p] == 'X'; p++)
                    flag[i][p] = 1;
                for (int p = j;p >= 0 && board[i][p] == 'X' ; p--)
                    flag[i][p] = 1;

            }
        return cnt;
    }
};
