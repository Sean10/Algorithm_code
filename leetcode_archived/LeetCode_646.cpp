class Solution {
public:
    int findLongestChain(vector<vector<int>>& pairs) {
        sort(pairs.begin() ,pairs.end(), [](const vector<int> &p1, const vector<int> &p2){\
                                           return p1[0] == p2[0] ? p1[1] < p2[1] : p1[0] < p2[0];});
        vector<int> dp(pairs.size()+1, 1);
        for (int i = 1;i < pairs.size(); i++)
        {
            // cout << pairs[i][0] << " " << pairs[i][1] << endl;
            int j = i -1;
            for (; j >= 0 && pairs[i][0] <= pairs[j][1];j--);

            if (j >= 0)
            {
                // cout << j << endl;
                dp[i] = max(dp[j] +1, dp[i]);
            }
        }
        return dp[pairs.size()-1];
    }
};
