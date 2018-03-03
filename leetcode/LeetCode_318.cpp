class Solution {
public:
    int maxProduct(vector<string>& words) {
        vector<int> mask(words.size());

        int ans = 0;
        for (int i = 0;i < words.size(); i++)
        {
            for (auto ch: words[i])
                mask[i] |= 1 << (ch - 'a');

            for (int j = 0; j < i; j++)
                if (! (mask[i] & mask[j]))
                    ans = max(ans, (int)words[i].size() * (int)words[j].size());
        }
        return ans;
    }
};
