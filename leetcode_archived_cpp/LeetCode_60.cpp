class Solution {
public:
    string getPermutation(int n, int k) {
        string dict(9, 0);
        iota(dict.begin(), dict.end(), '1');

        vector<int> table(10,1);
        for(int i = 1;i < 10;i++)
            table[i] = table[i-1]* i;

        k--;

        string ans;
        for(int i = n-1;i >= 0;i--)
        {
            int select = k/table[i];
            k %= table[i];
            ans.push_back(dict[select]);
            dict.erase(next(dict.begin(), select));
        }
        return ans;
    }
};


class Solution {
public:
    string getPermutation(int n, int k) {
        if(n > 9)
            n = 9;

        vector<string> ans;
        vector<bool> flag(n+1,false);
        helper(n ,{}, ans, flag);
        return ans[(k-1)%ans.size()];
    }

    void helper(int n, string temp, vector<string>& ans, vector<bool> flag)
    {
        if(temp.size() == n)
        {
            ans.push_back(temp);
            //cout << temp;
            return;
        }

        for(int i = 1;i <= n; i++)
        {
            if(flag[i])
                continue;
            temp.push_back('0'+i);
            flag[i] = true;
            helper(n, temp, ans, flag);
            flag[i] = false;
            temp.pop_back();
        }
    }
};
