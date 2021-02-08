class Solution {
public:

    // Encodes a URL to a shortened URL.
    string encode(string longUrl) {
        size_t n = h(longUrl);
        string s = "http://tinyurl.com/"+to_string(n);
        // cout << s << endl;
        map_[s] = longUrl;
        return s;
    }

    // Decodes a shortened URL to its original URL.
    string decode(string shortUrl) {
        return map_[shortUrl];
    }

    private:
    hash<string> h;
    unordered_map<string, string> map_;
};

// Your Solution object will be instantiated and called as such:
// Solution solution;
// solution.decode(solution.encode(url));
