class Solution {
public:
    int leastBricks(vector<vector<int>>& wall) {
        int ans = wall.size(), leng = wall.size();

        unordered_map<int, int> edge;
        for (auto rows: wall)
        {
            for (int i = 0, width = 0;i < rows.size()-1; i++)
            {
                width += rows[i];
                edge[width] += 1;
            }
        }

        for (auto e: edge)
        {
            ans = min(ans, leng - e.second);
            // cout << e.second;
        }

        return ans;
    }
};
