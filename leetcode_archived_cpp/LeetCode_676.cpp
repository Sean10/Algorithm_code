class MagicDictionary {
public:
    /** Initialize your data structure here. */
    MagicDictionary() {

    }

    /** Build a dictionary through a list of words */
    void buildDict(vector<string> dict) {
        for(auto i: dict)
            s.insert(i);
    }

    /** Returns if there is any word in the trie that equals to the given word after modifying exactly one character */
    bool search(string word) {
        int n = word.size();
        for(auto& i: word)
        {
            char c = i;
            for (int j = 0;j < 26;j ++)
            {
                if (c == 'a'+j) continue;
                i = 'a'+j;
                if(s.count(word))
                    return true;
            }
            i = c;
        }
        return false;
    }

    private:
    unordered_set<string> s;
};

/**
 * Your MagicDictionary object will be instantiated and called as such:
 * MagicDictionary obj = new MagicDictionary();
 * obj.buildDict(dict);
 * bool param_2 = obj.search(word);
 */
