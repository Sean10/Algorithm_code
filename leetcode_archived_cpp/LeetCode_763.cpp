class Solution {
public:
    vector<int> partitionLabels(string S) {
        unordered_map<char, int> flag;
        for(int i = 0;i < S.size();i++)
        {
            flag[S[i]] = i;
        }

        vector<int> ans;
        int start = 0, partition = 0, k = 0;
        while(k < S.size())
        {
            partition = flag[S[k]];
            while(k < partition)
            {
                partition = max(flag[S[k++]], partition);
            }
            ans.push_back(partition-start+1);
            start = ++k;
        }
        return ans;
    }
};
