class Solution {
public:
    int strStr(string haystack, string needle) {
        if(needle == "") return 0;
        int ans = haystack.find(needle);
        return ans >= haystack.size() ? -1 : ans;

    }
};
