class Solution {
public:
    bool canVisitAllRooms(vector<vector<int>>& rooms) {
        int m = rooms.size();
        queue<int> q_;
        vector<int> flag(m , 0);
        q_.push(0);
        for (int i = 0;!q_.empty(); i = q_.front())
        {
            q_.pop();
            if (flag[i] == 1)
                continue;
            flag[i] = 1;
            for (int j = 0 ;j < rooms[i].size(); j++)
            {
                q_.push(rooms[i][j]);
            }
                
        }
        
        for (int i = 0;i < m; i++)
        {
            if (flag[i] == 0)
                return false;
        }
        return true;
    }
};