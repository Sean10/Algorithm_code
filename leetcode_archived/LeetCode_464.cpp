class Solution {
public:
    bool canIWin(int maxChoosableInteger, int desiredTotal) {
        if (desiredTotal <= maxChoosableInteger)
            return true;
        if (maxChoosableInteger * (maxChoosableInteger + 1)/2 < desiredTotal)
            return false;
        unordered_map<int, int> mem;

        return bf(~0<<maxChoosableInteger, maxChoosableInteger, desiredTotal, mem);

    }

    int bf(int k, int m, int t, unordered_map<int, int>& mem)
    {
        if (t <= 0)
            return 0;

        auto x = mem.find(k);
        if (x != mem.end())
            return x->second;

        for (int i = 0; i < m; i++)
        {
            int temp = 1 << i;
            if (k & temp)
                 continue;
            k |= temp;
            if (!bf(k, m, t-i-1, mem))
                return mem[k^temp] = 1;
            k ^= temp;
        }
        return mem[k] = 0;
    }

};

// TLE
class Solution {
public:
    bool canIWin(int maxChoosableInteger, int desiredTotal) {
        if (desiredTotal <= maxChoosableInteger)
            return true;
        cout << ~0 << endl;
        cout << (~0 << maxChoosableInteger) << endl;
        return bf(~0<<maxChoosableInteger, maxChoosableInteger, desiredTotal);
    }

    int bf(unsigned int k, int m, int t)
    {
        if (t <= 0)
            return 0;

        for (int i = 0; i < m; i++)
        {
            int temp = 1 << i;
            if (k & temp)
                 continue;
            k |= temp;
            if (!bf(k, m, t-i-1))
                return 1;
            k ^= temp;
        }
        return 0;
    }

};
