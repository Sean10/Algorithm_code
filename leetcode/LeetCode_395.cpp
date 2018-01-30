class Solution {
public:
    int longestSubstring(string s, int k) {
        unordered_map<char, int> cnt;
        int n = s.size();
        for(auto i: s)
            cnt[i]++;

        int mid = 0;
        while(mid < n && cnt[s[mid]] >= k) mid++;
        if(mid == n) return mid;
        int left = longestSubstring(s.substr(0, mid), k);
        while(mid < n && cnt[s[mid]] < k) mid++;
        int right = longestSubstring(s.substr(mid), k);
        return max(left, right);
    }
};

class Solution {
public:
    int longestSubstring(string s, int k) {
        return maxStr(s, k, 0, s.size());
    }

    int maxStr(string s, int k, int first, int last)
    {
        int cnt[26] = {0};
        for(int j = first;j < last;j++)
            cnt[s[j]-'a']++;

        int max_len = 0;
        for(int j = first;j < last;)
        {
            while (j < last && cnt[s[j]-'a']<k) ++j;
            if (j == last) break;
            int l = j;
            while (l < last && cnt[s[l]-'a']>=k) ++l;
            //all chars appear more than k times
            if (j == first && l == last) return last-first;
            max_len = max(max_len, maxStr(s, k, j, l));
            j = l;
        }
        return max_len;

    }
};
