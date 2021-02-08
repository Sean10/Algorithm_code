// 组合数学
//
class Solution {
public:
    int uniquePaths(int m, int n) {
        long long ans = 1;

        for(int i = 1;i <= n-1; i++)
            ans =ans* (double)(m-1+i)/(double)(i);
        return (int)ans;
    }
};

// 记忆化搜索
//
class Solution {
public:
    int uniquePaths(int m, int n) {
        vector<vector<int>> flag(m);
        for(int i = 0;i < m;i++)
        {
            flag[i].resize(n, 0);
        }
        flag[0][0] = 1;


        for(int i = 0;i < m; i++)
        {
            for(int j = 0;j < n;j++)
            {
                if(i == 0 || j == 0)
                    flag[i][j] = 1;

                if(i-1 >= 0 && j-1 >= 0)
                    flag[i][j] = flag[i-1][j]+ flag[i][j-1];
            }
        }

        return flag[m-1][n-1];
    }
};



// 递归方法 TLE
//
class Solution {
public:
    int uniquePaths(int m, int n) {
        int cnt = 0;
        helper(cnt, m, n);
        return cnt;
    }

    void helper(int& cnt, int m, int n)
    {
        if(m == 1 && n == 1)
            cnt ++;
        if(m < 1 || n < 1)
            return ;

        helper(cnt, m-1,n);
        helper(cnt, m, n-1);
    }
};
