class Solution {
public:
    vector<vector<int>> generate(int numRows) {

        vector<vector<int>> ans;

        if(numRows < 1)
            return ans;

        ans.push_back({1});

        for(int i = 1;i < numRows; i++)
        {
            vector<int> temp(i+1, 0);
            temp[0] = ans[i-1][0];
            temp[i] = ans[i-1][i-1];
            for(int j = 1;j < i; j++)
            {
                temp[j] = ans[i-1][j-1] + ans[i-1][j];
            }
            ans.push_back(temp);
        }
        return ans;
    }
};
