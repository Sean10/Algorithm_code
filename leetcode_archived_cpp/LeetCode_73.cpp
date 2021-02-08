class Solution {
public:
    void setZeroes(vector<vector<int>>& matrix) {
        if (matrix.size() < 1 || matrix[0].size() < 1)
            return ;

        vector<int> rows, cols;
        for(int i = 0;i < matrix.size(); i++)
        {
            for(int j = 0;j < matrix[0].size();j++)
            {
                if(matrix[i][j] == 0)
                {
                    rows.push_back(i);
                    cols.push_back(j);
                }
            }
        }
        for(int i = 0;i < matrix.size(); i++)
            for(int j = 0;j < cols.size(); j++)
            {
                matrix[i][cols[j]] = 0;
            }

        for(int i = 0;i < matrix[0].size(); i++)
            for(int j = 0;j < rows.size(); j++)
                matrix[rows[j]][i] = 0;
    }
};
