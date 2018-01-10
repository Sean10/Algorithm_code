class Solution {
public:
    void solve(vector<vector<char>>& board) {
        int rows = board.size();
        if(rows == 0)
            return ;
        int cols = board[0].size();

        for(int i = 0;i < rows;i++)
        {
            BFS(board,i,0, '1');
            BFS(board,i, cols-1, '1');
        }

        for(int j = 0;j < cols;j++)
        {
            BFS(board,0, j, '1');
            BFS(board,rows-1, j, '1');
        }

        for(int i = 0;i < rows;i++)
        {
            for(int j = 0;j < cols;j++)
                cout << board[i][j];
            cout << endl;
        }

        for(int i = 0;i < rows;i++)
            for(int j = 0;j < cols;j++)
            {
                if(board[i][j] == 'O')
                    board[i][j] = 'X';
            }

        for(int i = 0;i < rows;i++)
            for(int j = 0;j < cols;j++)
            {
                if(board[i][j] == '1')
                    board[i][j] = 'O';
            }
    }

    void BFS(vector<vector<char>>& board,int x, int y, char target)
    {
        if(board[x][y] == 'X')
                return ;

        int dir[][2] = {{-1,0},{1,0},{0,-1},{0,1}};
        int rows = board.size();
        int cols = board[0].size();
        board[x][y] = target;
        queue<pair<int, int>> q;
        q.push(make_pair(x, y));
        while(!q.empty())
        {
            int tx = q.front().first;
            int ty = q.front().second;
            q.pop();
            for(int i = 0;i < 4; i++)
            {
                int nx = tx + dir[i][0];
                int ny = ty + dir[i][1];

                if(nx >= 0 && nx < rows && ny >= 0 && ny < cols && board[nx][ny] == 'O')
                {
                    q.push(make_pair(nx,ny));
                    board[nx][ny] = target;
                }
            }
        }
    }
};

# seond way


class Solution {
public:
    void solve(vector<vector<char>>& board) {
        int rows = board.size();
        if(rows == 0)
            return ;
        int cols = board[0].size();
        for(int i = 0;i < rows;i++)
        {
            DFS(board,i,0, '1');
            DFS(board,i, cols-1, '1');
        }

        for(int j = 0;j < cols;j++)
        {
            DFS(board,0, j, '1');
            DFS(board,rows-1, j, '1');
        }

        for(int i = 0;i < rows;i++)
            for(int j = 0;j < cols;j++)
            {
                if(board[i][j] == 'O')
                    board[i][j] = 'X';
            }

        for(int i = 0;i < rows;i++)
            for(int j = 0;j < cols;j++)
            {
                if(board[i][j] == '1')
                    board[i][j] = 'O';
            }
    }

    void DFS(vector<vector<char>>& board,int x, int y, char target)
    {
        int dir[][2] = {{-1,0},{1,0},{0,-1},{0,1}};

        int rows = board.size();
        int cols = board[0].size();
        if(board[x][y] == 'O')
        {
            board[x][y] = target;
            for(int i = 0;i < 4; i++)
            {
                int nx = x + dir[i][0];
                int ny = y + dir[i][1];

                if(nx >= 0 && nx < rows && ny >= 0 && ny < cols && board[nx][ny] == 'O')
                {
                    DFS(board,nx,ny,'1');
                }
            }
        }
    }
};
