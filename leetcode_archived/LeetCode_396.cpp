class Solution {
public:
    int maxRotateFunction(vector<int>& A) {
        int n = A.size(),max_num = INT_MIN;
        if(n == 0)
            return 0;
        int F = 0, sum_A = 0;
        for(int i = 0;i < n;i++)
        {
            F += i*A[i];
            sum_A += A[i];
        }
        max_num = max(max_num, F);

        for(int i = 0;i < n;i++)
        {
            F -= sum_A;
            F += A[i]*n;
            max_num = max(F, max_num);
        }

        return max_num;

    }
};
