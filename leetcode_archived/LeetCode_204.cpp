
class Solution {
public:
    int countPrimes(int n) {
        if (n <= 2)
            return 0;

        int cnt = 1;
        int mid = sqrt(n);
        vector<bool> flag(n, false);

        for(int i = 3;i < n;i += 2)
        {
            if(flag[i])
                continue;

            cnt ++;
            if(i > mid)
                continue;
            for(int j = i*i; j < n;j += i)
                flag[j] = true;

        }
        return cnt;
    }
};


class Solution {
public:
    int countPrimes(int n) {
        int cnt = 0;

        for(int i = 2;i < n;i++)
        {
            int j = 0;
            for(j = 2;j*j <= i; j++)
            {
                if(i % j == 0)
                    break;
            }
            if(j*j > i)
                cnt ++;
        }
        return cnt;
    }
};
