class Solution {
public:
    vector<int> diffWaysToCompute(string input) {
        // if(input.empty())
        //     return {};
        vector<int> ans;
        for(int i = 0;i < input.size(); i++)
        {
            char ch = input[i];
            //cout << ch;
            if(!ispunct(ch))
                continue;
            cout << ":"<<ch;
            //vector<int> temp1 = diffWaysToCompute(input.substr(0, i-1));
            //vector<int> temp2 = diffWaysToCompute(input.substr(i+1));
            for(int x: diffWaysToCompute(input.substr(0, i)))
                for(int y: diffWaysToCompute(input.substr(i+1)))
                {
                    ans.push_back(ch == '+' ? x+y : ch == '-' ? x-y : x*y);
                    cout << x << ch << y << endl;
                }
        }
        return !ans.empty() ? ans : vector<int>{atoi(input.c_str())};
    }
};
