class Solution {
public:
    int matrixScore(vector<vector<int>>& A) {
        int m = A.size(), n = A[0].size();
        
        
        
        for (int i = 0;i < m; i++)
        {
            if (A[i][0] == 0)
            {
                for (int j = 0;j < n; j++)
                    A[i][j] ^= 1;
            }
        }
        
        for (int j = 1;j < n; j++)
        {
            int cnt = 0;
            for (int i = 0;i < m; i++)
                cnt += A[i][j];
            
            if (cnt > (m >> 1))
                continue;
            
            for (int i = 0;i < m; i++)
            {
                A[i][j] ^= 1;
            }  
        }
        
        int ans = 0;
        int unit = 1;
        for (int j = n-1; j >= 0;j --)
        {
            for (int i = 0; i < m; i++)
            {
                ans += A[i][j]*unit;
            }
            unit = (unit << 1);
        }
        
        return ans;
    }
};
