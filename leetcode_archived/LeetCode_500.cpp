class Solution {
public:
    vector<string> findWords(vector<string>& words) {
        map<char,int> map_;
        init(map_);
        vector<string> ans;

        bool flag = true;
        for(int i = 0;i < words.size();i ++)
        {
            for(int j = 0;j < words[i].size()-1; j++)
            {
                if(map_[tolower(words[i][j])] != map_[tolower(words[i][j+1])])
                {
                    flag = false;
                    cout << i << j << endl;
                    cout << map_[tolower(words[i][j])] << '\t' << map_[tolower(words[i][j+1])] << endl;
                    break;
                }

            }

            if(flag)
            {
                ans.push_back(words[i]);
            }else
            {
                flag = true;
            }
        }
        return ans;
    }

    void init(map<char, int>& map_)
    {
        vector<string> temp = {"qwertyuiop","asdfghjkl","zxcvbnm"};
        for(int i = 0;i < 3;i++)
        {
            for(int j = 0;j < temp[i].size(); j++)
            {
                map_[temp[i][j]] = i;
            }
        }
    }
};
