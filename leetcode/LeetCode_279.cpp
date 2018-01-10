class Solution {
public:
    int numSquares(int n) {
        set<int> ans = {n};
        vector<int> list;
        int cnt = 0;
        for (int i = 1;i*i <= n; i++)
            list.push_back(i*i);
        while(!ans.empty())
        {
            cnt += 1;
            set<int> temp;
            for (auto i: ans)
            {
                for(auto j:list)
                {
                    if( i == j)
                        return cnt;
                    if (i < j)
                        break;
                    temp.insert(i-j);
                }
            }
            ans = temp;
        }
        return cnt;
    }
};
