class Solution {
public:
    int countArrangement(int N) {
        vector<int> ans;
        for(int i = 0;i < N; i++)
            ans.push_back(i+1);
        return helper(N, ans);
    }

    int helper(int N, vector<int> ans)
    {
        if(N < 2)
            return 1;
        int cnt = 0;
        for(int i = 0;i < N; i++)
        {
            if(ans[i]%N == 0 || N%ans[i] == 0)
            {
                swap(ans[i], ans[N-1]);
                cnt += helper(N-1, ans);
                swap(ans[i], ans[N-1]);
            }
        }
        return cnt;
    }
};
