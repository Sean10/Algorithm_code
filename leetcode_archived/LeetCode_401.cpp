class Solution {
public:

    const vector<int> chart={1,2,4,8,1,2,4,8,16,32};

    vector<string> readBinaryWatch(int num) {

        vector<string> ans;
        helper(ans, make_pair(0, 0), num, 0);
        return ans;
    }

    void helper(vector<string>& ans, pair<int, int> time, int num, int start)
    {
        if(num == 0)
        {
            ans.push_back(to_string(time.first)+(time.second < 10 ? ":0" : ":") + to_string(time.second));
            return ;
        }

        for(int i = start; i < chart.size(); i++)
        {
            if(i < 4)
            {
                time.first += chart[i];
                if(time.first < 12) helper(ans, time, num-1, i+1);
                time.first -= chart[i];
            }
            else
            {
                time.second += chart[i];
                if(time.second < 60) helper(ans, time, num-1, i+1);
                time.second -= chart[i];
            }
        }
    }
};

class Solution {
public:
    vector<string> readBinaryWatch(int num) {
        vector<string> ans;


        for(int h = 0;h < 12; h++)
            for(int m = 0;m < 60; m++)
                if(bitset<10>(h << 6 | m).count() == num)
                    ans.push_back(to_string(h)+(m < 10 ? ":0" : ":") + to_string(m));
        return ans;
    }
};
