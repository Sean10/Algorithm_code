class Solution {
public:
    vector<int> findall(string haystack, string needle) {
        vector<int> ans;
        int m = needle.size();

        if(m <= 0)
            return {};

        vector<int> f(m,0);
        int j = 0;
        process(needle, f);
        for(int i = 0;i < haystack.size(); i++)
        {
            while(j && haystack[i] != needle[j])
                j = f[j];
            if(haystack[i] == needle[j])
                j++;
            if(j == m)
            {
                ans.push_back(i-m+1);
                i = i-m+1;
            }
        }
        return ans;
    }

    void process(string s, vector<int>& f)
    {
        for(int i = 1; i < s.size()-1; i++)
        {
            int j = f[i];
            while(j && s[i] != s[j])
                j = f[j];
            f[i+1] = s[i] == s[j] ? j+1 : 0;

        }
    }

//     vector<int> findall(string S, string temp)
//     {
//         vector<int> ans;
//         for(int i = 0;i < S.size();)
//         {
//             bool flag = true, length = 0;
//             for(int j = 0;j < temp.size(); j++)
//             {
//                 if(S[i] != temp[j])
//                 {
//                     flag = false;
//                     break;
//                 }else
//                 {
//                     cout << i ;
//                     i++;
//                     length++;
//                 }
//             }


//             if(flag == true)
//                 ans.push_back(i-temp.size());
//             i++;
//             i -= length;
//             cout << "back:" << i;
//         }
//         return ans;
//     }

    string boldWords(vector<string>& words, string S) {
        vector<int> pos(S.size(),-1);
        for (int i=0; i<S.size(); ++i)
            for (int j=0; j<words.size(); ++j)
                if (i+words[j].size()-1<S.size() && S.substr(i,words[j].size())==words[j])
                    for (int k=i; k<i+words[j].size(); ++k) pos[k]=1;


        int flag = 0, start = 0, size = S.size();
        //cout << size;
        if(size > 0 && pos[size-1] == 1)
        {
            //cout << "size:" << size;
            S.insert(size, "</b>");
        }
        for(int i = size-2;i >= 0; i--)
        {
            //cout << pos[i] << pos[i+1] << endl;
            if(pos[i] == 1 && pos[i+1] == -1)
                S.insert(i+1, "</b>");
            else if(pos[i] == 1)
                continue;
            //cout << i;
            if(pos[i+1] == 1)
            {
                cout << "succeed";
                S.insert(i+1, "<b>");
            }
        }
        if(size > 0 && pos[0] == 1)
            S.insert(0, "<b>");
        return S;
    }
};
