class Solution {
public:
    int numJewelsInStones(string J, string S) {
        int ans = 0;
        sort(J.begin(), J.end());
        sort(S.begin(), S.end());
        for(int i = 0,j = 0;i < J.size() && j < S.size();)
        {
            if(J[i] == S[j])
            {
                j++;
                ans ++;
            }
            else if(J[i] < S[j])
                i++;
            else
                j++;

        }
        return ans;
    }
};
