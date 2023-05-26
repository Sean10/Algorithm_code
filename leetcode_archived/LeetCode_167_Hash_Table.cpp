class Solution {
public:
    vector<int> twoSum(vector<int>& numbers, int target) {
        map<int,int> list;
        map<int,int>::iterator iter;
        vector<int> ans(2,0);
        for(int i = 0;i < numbers.size();i++)
        {
            list.insert(pair<int,int>(numbers[i],i));
        }

        for(int i = 0;i < numbers.size();i++)
        {
            int complement = target - numbers[i];
            iter = list.find(complement);
            if(iter != list.end() && iter->second != i)
            {
                ans[0] = i+1;
                ans[1] = iter->second+1;
                sort(ans.begin(),ans.end());
                return ans;
            }
        }
    }
};
