class Solution {
public:
    bool judgeSquareSum(int c) {
        for (int i = 0;i <= sqrt(c); i++)
        {
            int t = sqrt(c-i*i);
            if (t*t+i*i == c)
                return true;
        }
        return false;
    }
};

class Solution {
public:
    bool judgeSquareSum(int c) {
        set<int> set_;

        for (int i = 0;i <= sqrt(c); i++)
        {
            set_.insert(i*i);
            if (set_.find(c-i*i) != set_.end())
                return true;
        }
        return false;
    }
};

class Solution {
public:
    bool judgeSquareSum(int c) {
        unordered_set<int> set_;

        for (int i = 0;i <= sqrt(c); i++)
        {
            set_.insert(i*i);
            if (set_.find(c-i*i) != set_.end())
                return true;
        }
        return false;
    }
};
