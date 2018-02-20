class Solution {
public:
    int nthSuperUglyNumber(int n, vector<int>& primes) {
        vector<int> ans(n, INT_MAX), index(primes.size(), 0);
        ans[0] = 1;
        for (int i = 1;i < n; i++)
        {
            for (int j = 0; j < primes.size(); j++)
                ans[i] = min(ans[i], ans[index[j]]*primes[j]);

            for (int j = 0; j < primes.size(); j++)
                index[j] += ans[i] == ans[index[j]]*primes[j];
        }

        return ans[n-1];
    }
};
