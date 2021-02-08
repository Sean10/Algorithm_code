// fibonacci 

class Solution {
public:
    int climbStairs(int n) {
        if(n <= 0)
            return 0;
        if(n == 1)
            return 1;
        if(n == 2)
            return 2;

        int sum = 0, one_step = 2, two_step = 1;
        for(int i = 2;i < n; i++)
        {
            sum = one_step+two_step;
            two_step = one_step;
            one_step = sum;
        }
        return sum;
    }
};

// 回溯算法 TLE
//
class Solution {
public:
    int climbStairs(int n) {
        int ans = 0;
        helper(n, ans);
        return ans;
    }

    void helper(int n, int& ans)
    {
        if (n == 0)
        {
            ans += 1;
            return ;
        }
        for(int i = 1;i <= 2;i++)
        {
            if (n < i)
                return ;
            helper(n-i, ans);
        }
    }
};
