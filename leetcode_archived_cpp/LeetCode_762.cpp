class Solution {
public:
    int countPrimeSetBits(int L, int R) {
        int cnt = 0;
        set<int> prime = {2, 3, 5, 7, 11, 13, 17, 19};
        for (int i = L; i <= R; i++)
        {
            int temp = i;
            int temp_count = 0;
            while (temp)
            {
                if (temp&1)
                    temp_count++;
                temp >>= 1;
            }
            if (prime.find(temp_count) != prime.end())
                cnt++;
        }
        return cnt;
    }
};
