class Solution {
public:
    int countNumbersWithUniqueDigits(int n) {
        if(n == 0)
            return 1;
        if(n > 10)
            n = 10;

        int cnt = 0;
        vector<bool> flag(10,false);
        vector<int> sear(10,INT_MIN);

        cnt += countNumbersWithUniqueDigits(n-1);
        for(int i = 1;i <= 9; i++)
        {
            flag[i] = true;
            if(sear[n-1] == INT_MIN)
                sear[n-1] = search(n-1, flag, sear);
            cnt += sear[n-1];
            flag[i] = false;
        }
        return cnt;

    }

    int search(int n, vector<bool> flag, vector<int> &sear)
    {
        if(n == 0)
            return 1;

        int cnt = 0;
        for(int i = 0;i <= 9; i++)
        {
            if(flag[i])
                continue;
            else
            {
                flag[i] = true;
                if(sear[n-1] == INT_MIN)
                    sear[n-1] = search(n-1, flag, sear);
                cnt += sear[n-1];
                flag[i] = false;
            }
        }
        return cnt;
    }
};
