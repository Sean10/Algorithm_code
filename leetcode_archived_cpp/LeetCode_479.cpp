class Solution {
public:
    int largestPalindrome(int n) {
        if (n == 1)
            return 9;
        int upper = pow(10,n)-1;
        int lower = pow(10,n-1);
        for (int i = upper; i >= lower; i--)
        {
            long candidate = build(i);
            for (long j = upper; j*j >= candidate;j--)
            {
                if (candidate%j == 0 && candidate/j <= upper)
                    return candidate%1337;
            }
        }
        return -1;
    }

    long build(int i)
    {
        string str(to_string(i));
        reverse(str.begin(), str.end());
        return stol(to_string(i) + str);

    }
};
