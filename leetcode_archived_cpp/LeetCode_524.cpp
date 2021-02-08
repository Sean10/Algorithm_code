class Solution {
public:
    static int comparex(string a, string b)
    {
        if(a.size() == b.size())
        {
            return a.compare(b) < 0;
        }else
        {
            return a.size() > b.size();
        }
    }

    string findLongestWord(string s, vector<string>& d) {
        sort(d.begin(), d.end(),comparex);

        for(int i = 0;i < d.size();i++)
        {
            //cout << d[i] << endl;
            int j = 0;
            for(int k = 0; k < s.size();k ++)
            {
                if(s[k] == d[i][j])
                    j++;
            }
            if(j == d[i].size())
                return d[i];
        }
        return "";
    }
};
