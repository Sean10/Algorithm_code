class Solution {
public:
    bool canPlaceFlowers(vector<int>& flowerbed, int n) {
        int pos = -1, cnt = 0;
        flowerbed.push_back(0);
        flowerbed.push_back(1);
        for (int i = 0;i < flowerbed.size(); i++)
        {
            if (flowerbed[i] == 0)
                continue;
            cnt = i - pos - 1;
            if(pos == -1 && cnt%2 == 0)
                n -= cnt/2;
            else if (cnt >= 3)
            {
                n -= (cnt-3)/2+1;
            }
            // cout << pos << ' ' << cnt << endl;

            if (n <= 0)
                return true;
            pos = i;

        }
        return false;
    }
};
